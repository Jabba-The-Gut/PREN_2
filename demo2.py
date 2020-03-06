import asyncio
from mavsdk import System


async def run():

    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered with UUID: {state.uuid}")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    asyncio.ensure_future(print_altitude(drone))


    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(5)

    print("-- Landing")
    await drone.action.land()


async def print_altitude(drone):
    """ Prints the altitude of the drone. THIS IS A DEBUG FUNCTION"""
    prev_alt = None
    async for pos in drone.telemetry.position():
        altitude = round(pos.relative_altitude_m)
        if altitude != prev_alt:
            prev_alt = altitude
            print(f"Altitude: {altitude}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())