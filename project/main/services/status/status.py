import pika
from main.const import const


class StatusService:
    def __init__(self):
        self.px4_running = False
        self.system_ok = False

        # Internal flags for this module to evaluate the system_ok flag
        self.__logic_service = False
        self.__data_processing_service = False
        self.__logging_service = False
        self.__init_service = False

        self.connection = None
        self.channel = None

    # Callback method
    def evaluate_status_flags(self, ch, method, properties, body):
        if self.system_ok:
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOGIC_STATUS_BINDING_KEY,
                body="status: system_ok: {0}".format(self.system_ok)
            )
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: system_ok: {0}".format(self.system_ok)
            )
        elif self.system_ok:
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOGIC_STATUS_BINDING_KEY,
                body="status: system_ok: {0}".format(self.system_ok)
            )
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: system_ok: {0}".format(self.system_ok)
            )
        if str(body).__contains__(const.INIT_PX4_FLAG_TRUE):
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: PX4 is started and running")
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.DATA_PROCESSING_BINDING_KEY,
                body=const.STATUS_PX4_FLAG_TRUE)
            self.px4_running = True
        elif str(body).__contains__(const.INIT_PX4_FLAG_FALSE):
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: PX4 did not start up successfully")
            self.px4_running = False
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.DATA_PROCESSING_BINDING_KEY,
                body="status: __px4_running: {0}".format(self.px4_running)
            )
        elif str(body).__contains__(const.STATUS_COMMANDS_UNSUCCESSFUL):
            self.px4_running = False
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.DATA_PROCESSING_QUEUE_NAME,
                body="status: __px4_running: {0}".format(self.px4_running)
            )
        elif str(body).__contains__(const.STATUS_DATAPROC_MODULE_FLAG_TRUE):
            self.__data_processing_service = True
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: data_processing module flag: {0}".format(self.__data_processing_service)
            )
        elif str(body).__contains__(const.STATUS_DATAPROC_MODULE_FLAG_FALSE):
            self.__data_processing_service = False
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: data_processing module flag: {0}".format(self.__data_processing_service)
            )
        elif str(body).__contains__(const.LOGIC_MODULE_FLAG_TRUE):
            self.__logic_service = True
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logic module flag: {0}".format(self.__logic_service)
            )
        elif str(body).__contains__(const.LOGIC_MODULE_FLAG_FALSE):
            self.__logic_service = False
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logic module flag: {0}".format(self.__logic_service)
            )
        elif str(body).__contains__(const.LOG_MODULE_FLAG_TRUE):
            self.__logging_service = True
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logging module flag: {0}".format(self.__logging_service)
            )
        elif str(body).__contains__(const.LOG_MODULE_FLAG_FALSE):
            self.__logging_service = False
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logging module flag: {0}".format(self.__logging_service)
            )
        elif str(body).__contains__(const.INIT_MODULE_FLAG_TRUE):
            self.__init_service = True
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: init module flag: {0}".format(self.__init_service)
            )
        elif str(body).__contains__(const.INIT_MODULE_FLAG_FALSE):
            self.__init_service = False
            self.channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: init module flag: {0}".format(self.__init_service)
            )

        self.system_ok = self.px4_running and self.__data_processing_service and self.__logging_service and self.__logic_service

        print("system_ok: %r, px4_running: %r, data_processing: %r, logging: %r, logic: %r" % (self.system_ok,
            self.px4_running, self.__data_processing_service, self.__logging_service, self.__logic_service))

    def run(self):
        """
        Contains the main logic for the status module
        """
        # Basic initialization of the rabbitMQ backend
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

        self.channel.queue_declare(const.STATUS_QUEUE_NAME, exclusive=False)

        self.channel.queue_bind(
            exchange='main', queue=const.STATUS_QUEUE_NAME, routing_key=const.STATUS_BINDING_KEY
        )

        self.channel.basic_consume(
            queue=const.STATUS_QUEUE_NAME, on_message_callback=self.evaluate_status_flags, auto_ack=True
        )
        print("Status Module running and waiting on messages to relay...")
        self.channel.start_consuming()
        self.connection.close()


def main():
    status = StatusService()
    status.run()
