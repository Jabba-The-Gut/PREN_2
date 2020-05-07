#!/usr/bin/env python3
import json
import threading
import time
from threading import Lock

import pika
from mavsdk import (OffboardError, PositionNedYaw)

from project.main.const import const
import atexit



def callbackStatus(ch, method, properties, body):
    message_parts = body.decode('utf8').split(":")

    if message_parts[2].__eq__(" True"):
        LogicStatus.systemStateOk = True
    else:
        LogicStatus.systemStateOk = False
    print("system_ok: %r" % LogicStatus.systemStateOk)

class LogicStatus(threading.Thread):

    systemStateOk = True

    def __init__(self):
        threading.Thread.__init__(self)
        self.connectionStatus = None
        self.channelStatus = None
        self.lock = Lock()
        self.channel = None

    def declareQueueStatus(self):
        self.connectionStatus = pika.BlockingConnection(
            pika.ConnectionParameters(host=const.CONNECTION_STRING))
        self.channel = self.connectionStatus.channel()
        self.channelStatus = self.connectionStatus.channel()
        # declare queue just for status messages (system_ok)
        self.channel.queue_declare(const.LOGIC_STATUS_QUEUE_NAME, exclusive=False)
        self.channel.queue_bind(
            exchange='main', queue=const.LOGIC_STATUS_QUEUE_NAME, routing_key=const.LOGIC_STATUS_BINDING_KEY
        )
        self.checkOverallStatus()

    def checkOverallStatus(self):
        print(' [*] Waiting for overall values. To exit press CTRL+C')
        self.channelStatus.basic_consume(queue=const.LOGIC_STATUS_QUEUE_NAME,
                                         on_message_callback=callbackStatus, auto_ack=True)
        self.channelStatus.start_consuming()

    def run(self):
        self.declareQueueStatus()

def main():
    thread1 = LogicStatus()
    thread1.start()



