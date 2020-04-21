import pika
from project.services.const import const
# Basic initialization of the rabbitMQ backend
connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
channel = connection.channel()
channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

result = channel.queue_declare(const.STATUS_QUEUE_NAME, exclusive=False)

binding_key = const.STATUS_BINDING_KEY

channel.queue_bind(
    exchange='main', queue=const.STATUS_QUEUE_NAME, routing_key=const.STATUS_QUEUE_NAME
)

px4_running = False
system_ok   = False


# Internal flags for this module to evaluate the system_ok flag

__logic_service = False
__data_processing_service = False
__logging_service = False

# Callback method
def evaluate_status_flags(ch, method, properties, body):
    global px4_running, __data_processing_service, __logic_service, __logging_service, system_ok
    system_ok = px4_running and __data_processing_service and __logging_service and __logic_service
    if not system_ok:
        channel.basic_publish(
            exchange=const.EXCHANGE,
            routing_key=const.LOGIC_QUEUE_NAME,
            body="status: system_ok: {0}".format(system_ok)
        )
    if str(body).__contains__(const.STATUS_INIT_PX4_FLAG_TRUE):
        print("PX4 is started and running")  # Log these in the future
        px4_running = True
    elif str(body).__contains__(const.STATUS_INIT_PX4_STATUS_FALSE):
        print("PX4 did not start up successfully")  # Log these in the future
        px4_running = False
        channel.basic_publish(
            exchange=const.EXCHANGE,
            routing_key=const.DATA_PROCESSING_QUEUE_NAME,
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
    elif str(body).__contains__(const.STATUS_DATAPROC_MODULE_FLAG_FALSE):
        __data_processing_service = False
        # Send a message here
    else:
        print("Default")

channel.basic_consume(
    queue=const.STATUS_QUEUE_NAME, on_message_callback=evaluate_status_flags, auto_ack=True
)
print("Status Module running and waiting on messages to relay...")
channel.start_consuming()
connection.close()