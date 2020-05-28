import asyncio
import json
import time

import aio_pika
from aio_pika import connect_robust, connect, Message, DeliveryMode, ExchangeType
from mavsdk import (OffboardError, VelocityBodyYawspeed, PositionNedYaw)

from project.main.const import const
import os
import project.main.services.logic.logMessage


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
        const.systemReady = True
        await flyToTravelHeight()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        await const.drone.action.disarm()
        return


async def flyToTravelHeight():
    await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, -0.4, 0.0))
    await asyncio.sleep(1)


async def generateCommandsForDrone(sensorData):
    height = json.loads(sensorData)["height"]
    sensor_front = json.loads(sensorData)["sensor_front"]
    sensor_side = json.loads(sensorData)["sensor_right"]

    heightState = checkHeightState(height)
    frontState = checkFrontState(sensor_front)
    sideState = checkSideState(sensor_side)

    if not const.systemStateOk:
        await const.drone.action.land()
        time.sleep(10000)
    if not const.systemReady:
        await takeoff()
        await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, -30))
        time.sleep(0.25)
    else:
        if (heightState == 2 and frontState == 2 and sideState == 2):
            #await log("forward")
            #task = asyncio.ensure_future(one(), loop=event_loop)
            await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(1.0, 0.0, 0.0, 0))
            print("forward 1m/s")
            # await asyncio.sleep(0.25)
        else:
            if (heightState == 0):
                #os.system("logMessage.py up")
             #   await log("up")
                print("up 0.4m/s")
                await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, -0.4, 0))
                # await asyncio.sleep(0.25)
            elif (heightState == 1):
                #os.system("logMessage.py down")
              #  await log("down")
                await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.4, 0))
                # await asyncio.sleep(0.25)
                print("down 0.4m/s")
            else:
                if (frontState == 1):
                    #os.system("logMessage.py left")
               #     await log("left")
                    await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, -90))
                    await asyncio.sleep(1)
                    print("left 90")
                else:
                    if (sideState == 0):
                        #os.system("logMessage.py right/forward")
                #        await log("right/forward")
                        await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(1.0, 0.0, -1, 0))
                        # await asyncio.sleep(0.25)
                        print("right/forward 1m/s left 1m/s forward")
                    elif (sideState == 1):
                        #os.system("logMessage.py left/forward")
                 #       await log("left/forward")
                        await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(1.0, 0.0, 1, 0))
                        # await asyncio.sleep(0.25)
                        print("left/forward 1m/s right 1m/s forward")
                    else:
                        #os.system("logMessage.py forward")
                  #      await log("forward")
                        await const.drone.offboard.set_velocity_body(VelocityBodyYawspeed(1.0, 0.0, 0.0, 0))
                        # await asyncio.sleep(3)
                        print("forward 1m/s")


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
    if sensor_right > const.MAX_RIGHT_DISTANCE:
        return 0
    elif sensor_right < const.MIN_RIGHT_DISTANCE:
        return 1
    else:
        return 2


async def log(message):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost"
    )

    async with connection:
        routing_key = const.LOG_BINDING_KEY

        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=routing_key,
        )
        await connection.close()

async def main(loop):
    connection = await connect_robust(
        "amqp://guest:guest@localhost", loop=loop
    )

    queue_name = const.LOGIC_QUEUE_NAME

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=True)
        await queue.bind(
            exchange='main', routing_key=const.LOGIC_BINDING_KEY)
        print(' [*] Waiting for sensor values. To exit press CTRL+C')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await generateCommandsForDrone(message.body)
                    if queue.name in message.body.decode():
                        break
