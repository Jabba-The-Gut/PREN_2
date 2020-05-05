#!/usr/bin/env python3
import json
import threading
import time
from threading import Lock

import pika
from mavsdk import (OffboardError, VelocityBodyYawspeed)
from project.main.const import const
import atexit
from project.main.services.logic import LogicStatus


def callback(ch, method, properties, body):
    # print(body)
    LogicSensor.generateCommandsForDrone(body)



connectionLog = pika.BlockingConnection(
    pika.ConnectionParameters(host=const.CONNECTION_STRING))
channelLog = connectionLog.channel()
channelLog.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')
lock = Lock()


def log(message):
    channelLog.basic_publish(
        exchange=const.EXCHANGE, routing_key=const.LOG_BINDING_KEY, body=message)


def main():
    thread1 = LogicSensor()
    thread1.start()


async def takeoff():
    await const.drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in const.drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered with UUID: {state.uuid}")
            break

    print("-- Arming")
    await const.drone.action.arm()

    print("-- Setting initial setpoint")
    await const.drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await const.drone.offboard.start()
        LogicSensor.systemReady = True
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        await const.drone.action.disarm()
        return

class LogicSensor(threading.Thread):
    systemReady = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.connection = None
        self.channel = None
        self.channelLog = None
        self.lock = Lock()


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

        if not (LogicStatus.systemStateOk):
            const.drone.action.land()
            time.sleep(10000)
        if not LogicSensor.systemReady:
            takeoff()
            time.sleep(1)
        else:
            if (heightState == 2 and frontState == 2 and sideState == 2):
                await const.drone.offboard.set_velocity_ned(VelocityBodyYawspeed(4.0, 0.0, 0.0, 0))
                log("await asyncio.sleep(0.25)")
            else:
                if (heightState == 0):
                    const.drone.offboard.set_velocity_nedVelocityBodyYawspeed((0.0, 0.0, -0.4, 0))
                    log("await asyncio.sleep(0.25)")
                elif (heightState == 1):
                    const.drone.offboard.set_velocity_ned(VelocityBodyYawspeed(0.0, 0.0, 0.4, 0))
                    log("await asyncio.sleep(0.25)")
                else:
                    if (frontState == 1):
                        const.drone.offboard.set_velocity_ned(VelocityBodyYawspeed(0.0, 0.0, 0.0, 360))
                        log("await asyncio.sleep(0.25)")
                    else:
                        if (sideState == 0):
                            const.drone.offboard.set_velocity_ned(VelocityBodyYawspeed(4.0, 0.4, 0.0, 0))
                            log("await asyncio.sleep(0.25)")
                        elif (sideState == 0):
                            const.drone.offboard.set_velocity_ned(VelocityBodyYawspeed(4.0, -0.4, 0.0, 0))
                            log("await asyncio.sleep(0.25)")
                        else:
                            const.drone.offboard.set_velocity_ned(VelocityBodyYawspeed(4.0, 0.0, 0.0, 0))
                            log("await asyncio.sleep(0.25)")

    # Return 0 means to low, return 1 means to high, return 2 means ok
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

