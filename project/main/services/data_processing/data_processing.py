import threading
import time

import pika
from main.const import const
from main.services.data_processing import i2c
from main.services.data_processing import ring_buffer
import atexit


class DataProcessingConsumer:
    """
    This class is used to consume messages from its queue. It uses polling to fetch messages
    with basic_get. This is some kind of hack, because the blocking character of start_consuming just
    caused problems...
    """

    def __init__(self, data_processing_service):
        """
        Initialize connection for consuming messages
        :param data_processing_service: service of type DataProcessingService
        """
        # declare service
        self.service = data_processing_service
        # setup connection details
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
        self._channel = self._connection.channel()
        # declare exchange
        self._channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')
        # declare queue
        self._channel.queue_declare(const.DATA_PROCESSING_QUEUE_NAME, exclusive=False)
        # create binding
        self._channel.queue_bind(
            exchange=const.EXCHANGE, queue=const.DATA_PROCESSING_QUEUE_NAME,
            routing_key=const.DATA_PROCESSING_BINDING_KEY
        )
        self.service = data_processing_service

        # start the consuming of the messages
        thread = threading.Thread(target=self.run, args=(), daemon=True)
        thread.start()

    def run(self):
        """
        Polls the queue for the data processing service, if there are any messages, pass it to the service
        :return: None
        """
        self._channel.basic_publish(exchange=const.EXCHANGE, routing_key=const.LOG_BINDING_KEY,
                                    body="data_processing:started to listen for status flags")
        while True:
            # if you set passive to true, you just check the status of the queue and get information about it
            check_queue = self._channel.queue_declare(queue=const.DATA_PROCESSING_QUEUE_NAME, passive=True)

            # just try to consume messages, if there are any
            if check_queue.method.message_count > 0:
                message = self._channel.basic_get(const.DATA_PROCESSING_QUEUE_NAME)
                # acknowledge it, because if not it stays in the queue
                self._channel.basic_ack(message[0].delivery_tag)
                self.service.handle_message(message[2])


class DataProcessingService:

    def __init__(self):
        self._px4_working = False
        self._blocked = False

        # reference to sensor data class
        self.sensor_data = i2c.I2cReader()

        # setup connection details
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
        self._connection.add_on_connection_blocked_callback(callback=self.connection_blocked)
        self._connection.add_on_connection_unblocked_callback(callback=self.connection_unblocked)

        self._channel = self._connection.channel()
        # declare exchange
        self._channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')
        # declare queue
        self._channel.queue_declare(const.DATA_PROCESSING_QUEUE_NAME, exclusive=False)

        # create binding
        self._channel.queue_bind(
            exchange=const.EXCHANGE, queue=const.DATA_PROCESSING_QUEUE_NAME,
            routing_key=const.DATA_PROCESSING_BINDING_KEY
        )

        self._channel.basic_publish(exchange=const.EXCHANGE, routing_key=const.LOG_BINDING_KEY,
                                    body="data_processing:successfully connected to rabbitmq")

    def connection_blocked(self):
        """
        Get's called once connection is blocked
        :return: None
        """
        self._blocked = True

    def connection_unblocked(self):
        """
        Get's called once connection is unblocked (freed)
        :return: None
        """
        self._blocked = False

    def handle_message(self, message):
        """
        Handles incoming messages from the consumer object.
        Currently we only care about status messages, so we ignore everything else
        :param message: message content
        :return: None
        """
        if message.__eq__(const.STATUS_PX4_FLAG_TRUE):
            self._px4_working = True
        else:
            self._px4_working = False

    def run(self):
        """
        This is the core method of the data service. It contains the main logic
        :return: None
        """
        # send message to status that data_processing module is ready
        self._channel.basic_publish(
            exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY,
            body=const.STATUS_DATAPROC_MODULE_FLAG_TRUE)

        values_asked_for = 0
        # i need to check the error flag of the last 5 values
        buffer = ring_buffer.RingBuffer(5)

        while True:
            values_asked_for += 1
            print("px4_working: %r, blocked: %r" % (self._px4_working, self._blocked))

            if self._px4_working and not self._blocked:
                sensor_values = self.sensor_data.read_values()
                # append the error flag to the buffer
                buffer.append(sensor_values["error"])

                if sum(buffer.get()) == 0 and values_asked_for > 5:  # we get an 0 if one of the sensors has an error
                    # publish to status value that we have an error in sensor values
                    self._channel.basic_publish(
                        exchange=const.EXCHANGE, routing_key=const.LOG_BINDING_KEY, body="data_processing:sensor "
                                                                                         "error")
                else:
                    del sensor_values["error"]
                    # publish values to logic module
                    self._channel.basic_publish(
                        exchange=const.EXCHANGE, routing_key=const.LOGIC_BINDING_KEY,
                        body=sensor_values)
                    self._channel.basic_publish(
                        exchange=const.EXCHANGE, routing_key=const.LOG_BINDING_KEY,
                        body=str.format("data_processing:%r" % sensor_values))



    def at_exit(self):
        # send message to status that data_processing module is ready
        self._channel.basic_publish(
            exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY,
            body=const.STATUS_DATAPROC_MODULE_FLAG_FALSE)


def main():
    # start our data processing service
    service = DataProcessingService()

    # create consumer
    DataProcessingConsumer(service)

    atexit.register(service.at_exit)

    # start logic
    service.run()
