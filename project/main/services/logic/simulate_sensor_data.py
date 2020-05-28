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

arrayHeight = arr.array('d', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 120, 105, 101, 120, 110, 100, 120, 105, 101, 110, 100, 120, 105, 101])
arraySensorFront = arr.array('d', [300, 290, 280, 270, 241, 220, 200, 160, 130, 100, 80, 60, 40, 30, 20, 0, 220, 200, 160, 130, 100, 80, 60, 40, 30, 20, 0])
arraySensorRight = arr.array('d', [60, 60, 50, 80, 70, 90, 60, 40, 80, 110, 60, 40, 33, 55, 41, 88, 60, 40, 80, 110, 60, 40, 33, 55, 41, 88])

channel.exchange_declare(exchange='main', exchange_type='topic')


routing_key = 'logic'
x=0

f = open("logs_1.txt", "r")
time.sleep(5)
for x in f:
    firstDelPos = x.find("{")  # get the position of delimiter [
    secondDelPos = x.find("}")  # get the position of delimiter ]
    extractedString = x[firstDelPos - 1:secondDelPos + 1]  # get the string between two dels
    if extractedString == "":
        print("empty")
    else:
        time.sleep(0.25)
        channel.basic_publish(
           exchange='main', routing_key=const.LOGIC_BINDING_KEY, body=extractedString)
        print(" [x] Sent %r:%r" % (const.LOGIC_BINDING_KEY, extractedString))

