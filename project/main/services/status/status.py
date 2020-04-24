import pika
from main.const import const


def _run():
    """
    Contains the main logic for the status module
    """
    # Basic initialization of the rabbitMQ backend
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
    channel = connection.channel()
    channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

    channel.queue_declare(const.STATUS_QUEUE_NAME, exclusive=False)

    channel.queue_bind(
        exchange='main', queue=const.STATUS_QUEUE_NAME, routing_key=const.STATUS_BINDING_KEY
    )

    # Callback method
    def evaluate_status_flags(ch, method, properties, body):
        px4_running = False
        system_ok = False

        # Internal flags for this module to evaluate the system_ok flag
        __logic_service = False
        __data_processing_service = False
        __logging_service = False
        __init_service = False

        system_ok = px4_running and __data_processing_service and __logging_service and __logic_service
        print("px4_running: %r, data_processing: %r, logging: %r, logic: %r" % (px4_running, __data_processing_service, __logging_service, __logic_service))
        if not system_ok:
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOGIC_STATUS_BINDING_KEY,
                body="status: system_ok: {0}".format(system_ok)
            )
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: system_ok: {0}".format(system_ok)
            )
        if str(body).__contains__(const.STATUS_INIT_PX4_FLAG_TRUE):
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: PX4 is started and running")
            px4_running = True
        elif str(body).__contains__(const.STATUS_INIT_PX4_STATUS_FALSE):
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: PX4 did not start up successfully")
            px4_running = False
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.DATA_PROCESSING_BINDING_KEY,
                body="status: __px4_running: {0}".format(px4_running)
            )
        elif str(body).__contains__(const.STATUS_COMMANDS_UNSUCCESSFUL):
            px4_running = False
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.DATA_PROCESSING_QUEUE_NAME,
                body="status: __px4_running: {0}".format(px4_running)
            )
        elif str(body).__contains__(const.STATUS_DATAPROC_MODULE_FLAG_TRUE):
            __data_processing_service = True
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: data_processing module flag: {0}".format(__data_processing_service)
            )
        elif str(body).__contains__(const.STATUS_DATAPROC_MODULE_FLAG_FALSE):
            __data_processing_service = False
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: data_processing module flag: {0}".format(__data_processing_service)
            )
        elif str(body).__contains__(const.LOGIC_MODULE_FLAG_TRUE):
            __logic_service = True
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logic module flag: {0}".format(__logic_service)
            )
        elif str(body).__contains__(const.LOGIC_MODULE_FLAG_FALSE):
            __logic_service = False
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logic module flag: {0}".format(__logic_service)
            )
        elif str(body).__contains__(const.LOG_MODULE_FLAG_TRUE):
            __logging_service = True
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logging module flag: {0}".format(__logging_service)
            )
        elif str(body).__contains__(const.LOG_MODULE_FLAG_FALSE):
            __logging_service = False
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: logging module flag: {0}".format(__logging_service)
            )
        elif str(body).__contains__(const.INIT_MODULE_FLAG_TRUE):
            __init_service = True
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: init module flag: {0}".format(__init_service)
            )
        elif str(body).__contains__(const.INIT_MODULE_FLAG_FALSE):
            __init_service = False
            channel.basic_publish(
                exchange=const.EXCHANGE,
                routing_key=const.LOG_BINDING_KEY,
                body="status: init module flag: {0}".format(__init_service)
            )

    channel.basic_consume(
        queue=const.STATUS_QUEUE_NAME, on_message_callback=evaluate_status_flags, auto_ack=True
    )
    print("Status Module running and waiting on messages to relay...")
    channel.start_consuming()
    connection.close()


def main():
    _run()
