#!/usr/bin/env python

import pika
from mavsdk import System
from mavsdk import (OffboardError, PositionNedYaw)
import json
from project.const import const

drone = System()

HEIGHT_TO_FLIGHT_MIN = 90
HEIGHT_TO_FLIGHT_MAX = 110
MAX_RIGHT_DISTANCE = 30
MIN_RIGHT_DISTANCE = 10
MIN_FRONT_DISTANCE = 40


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=const.CONNECTION_STRING))
channel = connection.channel()

channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

logicQueue = channel.queue_declare(const.LOGIC_QUEUE_NAME, exclusive=False)

routingKey_log = "log"

channel.queue_bind(
    exchange='main', queue=const.LOGIC_QUEUE_NAME, routing_key=const.LOGIC_BINDING_KEY)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    # print(" [x] %r:%r" % (method.routing_key, body))
    generateCommandsForDrone(body)

def log(message):
    print(message)
    channel.basic_publish(
        exchange=const.EXCHANGE, routing_key=routingKey_log, body=message)

def generateCommandsForDrone(sensorData):
    height = json.loads(sensorData)["height"]
    sensor_front = json.loads(sensorData)["sensor_front"]
    sensor_side = json.loads(sensorData)["sensor_right"]

    heightState = checkHeightState(height)
    frontState = checkFrontState(sensor_front)
    sideState = checkSideState(sensor_side)

    if(heightState == 2 and frontState == 2 and sideState == 2):
        log("VelocityBodyYawspeed(4.0, 0.0, 0.0, 0)")
        log("await asyncio.sleep(0.25)")
    else:
        if(heightState == 0):
            log("VelocityBodyYawspeed(0.0, 0.0, -0.4, 0)")
            log("await asyncio.sleep(0.25)")
        elif (heightState == 1):
            log("VelocityBodyYawspeed(0.0, 0.0, 0.4, 0)")
            log("await asyncio.sleep(0.25)")
        else:
            if (frontState == 1):
                log("VelocityBodyYawspeed(0.0, 0.0, 0.0, 360)")
                log("await asyncio.sleep(0.25)")
            else:
                if(sideState == 0):
                    log("VelocityBodyYawspeed(4.0, 0.4, 0.0, 0)")
                    log("await asyncio.sleep(0.25)")
                elif(sideState == 0):
                    log("VelocityBodyYawspeed(4.0, -0.4, 0.0, 0)")
                    log("await asyncio.sleep(0.25)")
                else:
                    log("VelocityBodyYawspeed(4.0, 0.0, 0.0, 0)")
                    log("await asyncio.sleep(0.25)")

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
    queue=const.LOGIC_QUEUE_NAME, on_message_callback=callback, auto_ack=True)

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

