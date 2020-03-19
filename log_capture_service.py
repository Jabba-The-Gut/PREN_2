import pika
class LogCapture:

    def __init__(self, port):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(port))
        self.channel = self.connection.channel()

    def callback_debug(self, ch, method, properties, body):
        print(" [DEBUG Listener] Received %r" % body)

    def callback_error(self, ch, method, properties, body):
        print(" [ERROR Listener] Received %r" % body)

    def recv(self, q):
        self.channel.queue_declare(queue=q)
        if (q == 'debug'):
            self.channel.basic_consume(queue=q,
                                       auto_ack=True,
                                       on_message_callback=self.callback_debug)
        elif(q == 'error'):
            self.channel.basic_consume(queue=q,
                                       auto_ack=True,
                                       on_message_callback=self.callback_error)
        print('[RECEIVER]: Waiting for messages. Press CTRL-C to exit')
        self.channel.start_consuming()

if __name__ == '__main__':
    lcapture_debug = LogCapture('localhost')
    lcapture_debug.recv('error')
    lcapture_debug.recv('debug')
