import pika
from project.services.const import const

px4_running = False
system_ok   = False


# Internal flags for this module to evaluate the system_ok flag

__logic_service = 0
__data_processing_service = 0
__init_service = 0
__logging_service = 0

# Callback method


def evaluate_status_flags(ch, method, properties, body):
    if str(body).__contains__(const.STATUS_DATA_PROC_PX4_FLAG_TRUE):
        print("PX4 is running and the data processing service is running")
        global px4_running
        px4_running = True
    elif str(body).__contains__(const.STATUS_DATA_PROC_PX4_FLAG_FALSE):
        print("PX4 not running data processing should stop")
        global px4_running
        px4_running = False
    else:
        print("Default")

    global system_ok, px4_running, __data_processing_service
    __data_processing_service = 1
    system_ok = px4_running and (__data_processing_service == 1) # Will add other flags to this evaluation when necessary
    channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

    channel.queue_declare(const.LOGIC_QUEUE_NAME, exclusive=False)

    channel.queue_bind(
        exchange='main', queue=const.LOGIC_QUEUE_NAME, routing_key=const.LOGIC_QUEUE_NAME
    )

    message_body = "{0}".format(system_ok)

    channel.basic_publish(
        exchange=const.EXCHANGE,
        routing_key=const.LOGIC_QUEUE_NAME,
        body=message_body
    )



# Basic initialization of the rabbitMQ backend


connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
channel = connection.channel()
channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

result = channel.queue_declare(const.STATUS_QUEUE_NAME, exclusive=False)

binding_key = const.STATUS_BINDING_KEY

channel.queue_bind(
    exchange='main', queue=const.STATUS_QUEUE_NAME, routing_key=const.STATUS_QUEUE_NAME
)

channel.basic_consume(
    queue=const.STATUS_QUEUE_NAME, on_message_callback=evaluate_status_flags, auto_ack=True
)
print("Status Module running and waiting on messages to relay...")
channel.start_consuming()
connection.close()