import pika
from datetime import datetime
from main.const import const


def _run():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
    channel = connection.channel()
    channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

    result = channel.queue_declare(const.LOG_QUEUE_NAME, exclusive=False)

    channel.queue_bind(
        exchange='main', queue=const.LOG_QUEUE_NAME, routing_key=const.LOG_BINDING_KEY
    )

    print(' [*] Waiting for logs. To exit press CTRL-C')

    def callback(ch, method, properties, body):
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
            file.write(str(to_write))
            file.close()

    channel.basic_consume(
        queue=const.LOG_QUEUE_NAME, on_message_callback=callback, auto_ack=True
    )

    channel.start_consuming()


def main():
    _run()
