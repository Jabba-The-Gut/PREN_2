import pika
from datetime import datetime
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='main', exchange_type='topic')

result = channel.queue_declare('log', exclusive=False)
queue_name = result.method.queue

binding_key = '#.log.#'

channel.queue_bind(
    exchange='main', queue=queue_name, routing_key=binding_key
)

print(' [*] Waiting for logs. To exit press CTRL-C')

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    # Will write to file the log message here
    with open("logs.txt", "a+") as file:
        file.seek(0)
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        now = datetime.now()
        current = now.strftime("%H:%M:%S")
        to_write = str(current) + " " + str(body)
        file.write(str(to_write))
        file.close()



channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)

channel.start_consuming()