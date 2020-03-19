import pika

class Logger:

    def __init__(self, port):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(port))
        self.channel = self.connection.channel()

    def send_debug(self, msg):
        self.channel.queue_declare(queue='debug')
        self.channel.basic_publish(exchange='',
                                   routing_key='debug',
                                   body=msg)
        print('[DEBUG] Log: ' + msg + '!')

    def send_error(self, msg):
        self.channel.queue_declare(queue='error')
        self.channel.basic_publish(exchange='',
                                   routing_key='error',
                                   body=msg)
        print('[ERROR] Log: ' + msg + '!')

if __name__ == '__main__':
    log = Logger('localhost')
    log.send_debug('Hello World')
    log.send_error('No NO NO!')


