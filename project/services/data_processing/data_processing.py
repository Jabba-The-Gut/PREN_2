import threading
import time

import pika
from project.services.const import const


class DataProcessingConsumer:
    """
    This class is used to consume messages from its queue. It is
    a separate class because the start_consuming() method is blocking. This way,
    it can be outsourced to a different thread so the service can proceed
    """

    def __init__(self):
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def start_consuming(self, callback):
        """
        Start consuming messages, this method never exits
        :return: None
        """
        self._channel.basic_consume(
            queue=const.DATA_PROCESSING_QUEUE_NAME, on_message_callback=callback, auto_ack=True
        )
        self._channel.start_consuming()


class DataProcessingService:

    def __init__(self):
        self._sensor_working = False
        self._init_done = False
        self._logic_ready = False
        self._blocked = False

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

    def handle_message(self, channel, method, properties, message):
        """
        Handles incoming messages from the consumer object
        :param properties: properties of the message
        :param message: message content
        :return: None
        """
        print("received message %r %r %r %r" % (channel, method, properties, message))

    def start_consumer(self):
        """
        Starts the consuming of messages using a consumer object in a different thread
        :return: None
        """

        # callback method if consumer receives message
        def callback(channel, method, properties, body):
            self.handle_message(channel, method, properties, body)

        with DataProcessingConsumer() as consumer:
            consumer.start_consuming(callback=callback)

    def check_sensors(self):
        """
        Check if sensors are working
        :return: True if working, false if not
        """
        NotImplementedError

    def run(self):
        """
        This is the core method of the data service. It contains the main logic
        :return: None
        """
        while True:
            if self._logic_ready and self._init_done:
                if self.check_sensors():
                    comment = "Get sensor data and publish it"
                    print(comment)
                else:
                    comment = "Publish that sensors are fucked"
                    print(comment)

            # This value is just for testing purposes
            time.sleep(1)


def main():
    # start our data processing service
    service = DataProcessingService()

    # create consumer object with callback to data processing service, but on another thread thus not blocking
    consumer_thread = threading.Thread(target=service.start_consumer())
    consumer_thread.start()

    # let's start the magic
    service.run()

if __name__ == '__main__':
    main()
