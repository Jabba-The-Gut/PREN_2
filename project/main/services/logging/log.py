import pika
from datetime import datetime
from project.main.const import const
import atexit

buffered_logs = []
buffer_threshold = 20
"""
This is the logging service. It logs all messages that are sent to it from any of the other services and
outputs it to a file on the filesystem to be viewed later if need.
"""

def _run():
    """
    The main function of this service. The connection is established, queue set and the service is made ready
    for functionality here.
    :return:
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
    channel = connection.channel()
    channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

    result = channel.queue_declare(const.LOG_QUEUE_NAME, exclusive=False)

    channel.queue_bind(
        exchange='main', queue=const.LOG_QUEUE_NAME, routing_key=const.LOG_BINDING_KEY
    )

    def at_exit():
        # send message to status that log module is not ready
        channel.basic_publish(
            exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY,
            body=const.LOG_MODULE_FLAG_FALSE)

    atexit.register(at_exit)

    # send message to status that log module is ready
    channel.basic_publish(
        exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY,
        body=const.LOG_MODULE_FLAG_TRUE)


    print(' [*] Waiting for logs. To exit press CTRL-C')

    def callback(ch, method, properties, body):
        global buffered_logs, buffer_threshold
        print(" [x] %r:%r" % (method.routing_key, body.decode('utf8')))
        # Will write to file the log message here
        with open("logs.txt", "a+") as file:
            file.seek(0)
            data = file.read(100)
            if len(data) > 0:
                file.write("\n")
            now = datetime.now()
            current = now.strftime("%H:%M:%S")
            to_write = str(current) + " " + str(body.decode('utf8'))
            buffered_logs.append(to_write)
            if (len(buffered_logs) > buffer_threshold):
                for log in buffered_logs:
                    file.write(str(log))
            file.close()

    channel.basic_consume(
        queue=const.LOG_QUEUE_NAME, on_message_callback=callback, auto_ack=True
    )

    channel.start_consuming()


def main():
    _run()
