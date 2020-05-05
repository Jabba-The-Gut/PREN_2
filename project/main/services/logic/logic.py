#!/usr/bin/env python3
import json
import threading
import time
from threading import Lock

import pika
from mavsdk import (OffboardError, PositionNedYaw)
from mavsdk import System

from project.main.const import const
import atexit


def callback(ch, method, properties, body):
    # print(body)
    LogicSensor.generateCommandsForDrone(body)


def callbackStatus(ch, method, properties, body):
    message_parts = body.decode('utf8').split(":")

    if message_parts[2].__eq__(" True"):
        LogicSensor.systemStateOk = True
    else:
        LogicSensor.systemStateOk = False
    print("system_ok: %r" % LogicSensor.systemStateOk)


connectionLog = pika.BlockingConnection(
    pika.ConnectionParameters(host=const.CONNECTION_STRING))
channelLog = connectionLog.channel()
channelLog.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')
lock = Lock()


def log(message):
    channelLog.basic_publish(
        exchange=const.EXCHANGE, routing_key=const.LOG_BINDING_KEY, body=message)


class LogicStatus(threading.Thread):

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


class LogicSensor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.drone = System()
        self.connection = None
        self.channel = None
        self.channelLog = None
        self.lock = Lock()
        self.systemStateOk = True

    def run(self):
        self.declareQueueSensor()

    def declareQueueSensor(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=const.CONNECTION_STRING))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')
        self.channel.queue_declare(const.LOGIC_QUEUE_NAME, exclusive=False)
        self.channel.queue_bind(
            exchange='main', queue=const.LOGIC_QUEUE_NAME, routing_key=const.LOGIC_BINDING_KEY)

        def at_exit():
            # send message to status that logic module is not ready
            self.channel.basic_publish(
                exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY,
                body=const.LOGIC_MODULE_FLAG_FALSE)

        atexit.register(at_exit)

        # send message to status that logic module is ready
        self.channel.basic_publish(
            exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY,
            body=const.LOGIC_MODULE_FLAG_TRUE)

        self.readSensorValues()

    def readSensorValues(self):
        print(' [*] Waiting for sensor values. To exit press CTRL+C')
        self.channel.basic_consume(queue=const.LOGIC_QUEUE_NAME,
                                   on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def generateCommandsForDrone(sensorData):
        height = json.loads(sensorData)["height"]
        sensor_front = json.loads(sensorData)["sensor_front"]
        sensor_side = json.loads(sensorData)["sensor_right"]

        heightState = LogicSensor.checkHeightState(height)
        frontState = LogicSensor.checkFrontState(sensor_front)
        sideState = LogicSensor.checkSideState(sensor_side)

        if not (LogicSensor.systemStateOk):
            log("LogicSensor.drone.action.land()")
            time.sleep(5)
        if (heightState == 2 and frontState == 2 and sideState == 2):
            log("VelocityBodyYawspeed(4.0, 0.0, 0.0, 0)")
            log("await asyncio.sleep(0.25)")
        else:
            if (heightState == 0):
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
                    if (sideState == 0):
                        log("VelocityBodyYawspeed(4.0, 0.4, 0.0, 0)")
                        log("await asyncio.sleep(0.25)")
                    elif (sideState == 0):
                        log("VelocityBodyYawspeed(4.0, -0.4, 0.0, 0)")
                        log("await asyncio.sleep(0.25)")
                    else:
                        log("VelocityBodyYawspeed(4.0, 0.0, 0.0, 0)")
                        log("await asyncio.sleep(0.25)")

    # Return 0 means to low, return 1 means to hight, return 2 means ok
    def checkHeightState(height):
        if height < const.HEIGHT_TO_FLIGHT_MIN:
            return 0
        elif height > const.HEIGHT_TO_FLIGHT_MAX:
            return 1
        else:
            return 2

    def checkFrontState(sensor_front):
        if sensor_front < const.MIN_FRONT_DISTANCE:
            return 1
        else:
            return 2

    def checkSideState(sensor_right):
        if sensor_right < const.MAX_RIGHT_DISTANCE:
            return 0
        elif sensor_right > const.MIN_RIGHT_DISTANCE:
            return 1
        else:
            return 2

    async def takeoff(self):
        # getReadyCommands send to drone
        await self.drone.connect(system_address="udp://14540")
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

    def main(self):
        thread1 = LogicStatus()
        thread1.start()
        thread2 = LogicSensor()
        thread2.start()


def main():
    logic = LogicSensor()
    logic.main()
