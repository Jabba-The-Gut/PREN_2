#!/usr/bin/env python

from random import randint

import pika
import sys
import array as arr
import json
import time
import asyncio
from project.main.const import const

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

arrayHeight = arr.array('d', [0, 90, 101, 100, 120, 110, 100, 120, 105, 101, 110, 100, 120, 105, 101, 120, 110, 100, 120, 105, 101, 110, 100, 120, 105, 101])
arraySensorFront = arr.array('d', [300, 290, 280, 270, 241, 220, 200, 160, 130, 100, 80, 60, 40, 30, 20, 0, 220, 200, 160, 130, 100, 80, 60, 40, 30, 20, 0])
arraySensorRight = arr.array('d', [60, 60, 50, 80, 70, 90, 60, 40, 80, 110, 60, 40, 33, 55, 41, 88, 60, 40, 80, 110, 60, 40, 33, 55, 41, 88])

channel.exchange_declare(exchange='main', exchange_type='topic')


routing_key = 'logic'
x=0
while(x<15):
    print(arrayHeight[x])
    message = {
        "height": arrayHeight[x],
        "sensor_front": arraySensorFront[x],
        "sensor_right": arraySensorRight[x]
    }
    time.sleep(1)
    channel.basic_publish(
        exchange='main', routing_key=const.LOGIC_BINDING_KEY, body=json.dumps(message))
    print(" [x] Sent %r:%r" % (const.LOGIC_BINDING_KEY, json.dumps(message)))
    x=x+1
connection.close()



