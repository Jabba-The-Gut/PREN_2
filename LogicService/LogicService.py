#!/usr/bin/env python
import asyncio

import pika
from mavsdk import System
from mavsdk import (OffboardError, PositionNedYaw, VelocityBodyYawspeed)
import json

HEIGHT_TO_FLIGHT_MIN = 90
HEIGHT_TO_FLIGHT_MAX = 110
MAX_RIGHT_DISTANCE = 30
MIN_RIGHT_DISTANCE = 10
MIN_FRONT_DISTANCE = 10

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='main', exchange_type='topic')

logicQueue = channel.queue_declare('logic', exclusive=False)
queue_name = logicQueue.method.queue

loggerQueue = channel.queue_declare('log', exclusive=False)
queue_name = loggerQueue.method.queue

binding_key = '#.logic.#'

channel.queue_bind(
    exchange='main', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    # print(" [x] %r:%r" % (method.routing_key, body))
    generateCommandsForDrone(body)


def generateCommandsForDrone(sensorData):
    height = json.loads(sensorData)["height"]
    sensor_front = json.loads(sensorData)["sensor_front"]
    sensor_side = json.loads(sensorData)["sensor_right"]

    heightState = checkHeightState(height)
    frontState = checkFrontState(sensor_front)
    sideState = checkSideState(sensor_side)

    if(heightState == 2 and frontState == 2 and sideState == 2):
        print("going strait forward")
    else:
        if(heightState == 0):
            print("go up")
        elif (heightState == 1):
            print("go down")
        elif (heightState == 2):
            print("do nothing with height")
            if(frontState == 1):
                print("turn right")
            else:
                print("go forward")
                if(sideState == 0):
                    print("go left")
                elif(sideState == 0):
                    print("go right")
                else:
                    print("stay there")

#Return 0 means to low, return 1 means to hight, return 2 means ok
def checkHeightState(height):
    if height < HEIGHT_TO_FLIGHT_MIN:
        return 0
    elif height > HEIGHT_TO_FLIGHT_MAX:
        return 1
    else:
        return 2

def checkFrontState(sensor_front):
    if sensor_front < MIN_FRONT_DISTANCE:
        return 1
    else:
        return 2

def checkSideState(sensor_right):
    if sensor_right < MAX_RIGHT_DISTANCE:
        return 0
    elif sensor_right > MIN_RIGHT_DISTANCE:
        return 1
    else:
        return 2

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()


async def takeoff(self):
    # getReadyCommands send to drone
    await self.drone.connect(system_address="udp://:14540")
    drone = System()
    print("-- Arming")
    await self.drone.action.arm()

    print("-- Setting initial setpoint")
    await self.drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    try:
        await self.drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        print("-- Disarming")
        await self.drone.action.disarm()
        return
