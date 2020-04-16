import pika
from project.services.const import const

# Variables that keep track of the various important statuses. (i.e. Memory, PX4, Sensor, System)
__memory_ok = True
__px4_running = True
__sensor_ok = True
__system_ok = True


# mutator methods for other services to write to the above status flags
def change_memory_status(new_status : bool) -> None:
    global __memory_ok
    __memory_ok = new_status


def change_px4_status (new_status : bool) -> None:
    global __px4_running
    __px4_running = new_status


def change_sensor_status(new_status : bool) -> None:
    global __sensor_ok
    __sensor_ok = new_status


def change_system_status(new_status : bool) -> None:
    global __system_ok
    __system_ok = new_status


connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
channel = connection.channel()
channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

result = channel.queue_declare(const.STATUS_QUEUE_NAME, exclusive=False)

binding_key = const.STATUS_BINDING_KEY

channel.queue_bind(
    exchange='main', queue=const.STATUS_QUEUE_NAME, routing_key=const.STATUS_QUEUE_NAME
)

to_publish = "Memory Status {0}, PX4 Status {1}, Sensor Status {2}, System Status {3}".format(__memory_ok, __px4_running, __sensor_ok, __system_ok)
channel.basic_publish(exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY, body=to_publish)
print(" [x] Sent %r" % to_publish)
connection.close()