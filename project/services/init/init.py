import asyncio
import time

import pika
from mavsdk import System
from project.services.const import const


# that this service runs means that other things such
# as raspberry pi and power etc. are ok

async def run():
    # first we set up the pika connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=const.CONNECTION_STRING))
    channel = connection.channel()
    # this declares the exchange if it doesn't exist, otherwise it just checks it
    channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')

    channel.queue_declare(const.INIT_QUEUE_NAME, exclusive=False)

    channel.queue_bind(
        exchange='main', queue=const.INIT_QUEUE_NAME, routing_key=const.INIT_BINDING_KEY
    )

    # then we have to initialize the mavsdk-environment (mavsdk-server)
    system = System()
    # then we need to connect to it
    await system.connect()

    # loop through all connections and get the first that is connected
    async for state in system.core.connection_state():
        if state.is_connected:
            break

    # publish that drone is ready and connected
    channel.basic_publish(exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY, body="Drone connected",
                          properties=pika.BasicProperties(headers=const.INIT_HEADER_NAME))

    # loop that checks the connection state every second
    while True:
        for state in system.core.connection_state():
            if state.is_connected:
                channel.basic_publish(exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY, body="Drone connected",
                                      properties=pika.BasicProperties(headers=const.INIT_HEADER_NAME))
            else:
                channel.basic_publish(exchange=const.EXCHANGE, routing_key=const.STATUS_BINDING_KEY, body="Drone connection lost",
                                      properties=pika.BasicProperties(headers=const.INIT_HEADER_NAME))
        time.sleep(1)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


if __name__ == "__main__":
    main()
