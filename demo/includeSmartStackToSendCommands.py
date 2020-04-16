from collections import deque
import time
import threading
import asyncio
from this import s

from mavsdk import System
from mavsdk import (OffboardError, PositionNedYaw, VelocityBodyYawspeed)
from random import randint
'''
Need to add support for thread safe containers using threading.lock().aquire/.release()
'''

class Stack:
    def __init__(self, size):
        self.size = size
        self.buf = deque()
        self.buf_lock = threading.Lock()

    # Need to add logic to keep the buffer flowing. As in if there is no more space remove
    # earlier elements and make space
    # Almost like a sliding window
    # This sliding window type thing has been implemented below in @evaluate_relevant_data()
    def push_to_stack(self, to_push):
        if len(self.buf) < self.size:
            self.buf.append(to_push)
        else:
            print("Increase stack size to accomodate more elements")
    def pop_from_stack(self):
        try:
            return self.buf.pop()
        except IndexError:
            # print("Stack is empty cannot pop")
            return None

    def get_val(self, index):
        lock = threading.Lock()
        lock.acquire()
        try:
            return self.buf[index]
        finally:
            lock.release()


class CommsProtocol:

    def __init__(self, stack_size):
        self.stack = Stack(stack_size)
        self.stack.push_to_stack((0, 0, 0))
        self.min_front_val = 5
        self.min_height = 5
        self.min_side_val = 5
        self.history = 100

    def process_data(self, data):
        pass

    def evaluate_relevant_data(self, new_data):
        '''
        Evaluate the data to see if it is relevant or not.
        :param new_data:
        Convention for new_data is
        (height, side distance, front distance)
        :return: str
        ==== Error Codes Retured ====
        Code 1 : new_data was not of type tuple
        Code 2 : new_data had more or less than 3 elements in it
        '''
        if isinstance(new_data, tuple):
            if len(new_data) == 3:
                if self.stack.buf[-1][0] == new_data[0] or self.stack.buf[-1][1] == new_data[1] or self.stack.buf[-1][2] == new_data[2]:
                    del new_data
                    return 'Data Evaluated. Irrelevant data.'
                else:
                    self.stack.push_to_stack(new_data)
                    if len(self.stack.buf) > self.history:                  # This is the boundary variable for when to start sliding. Can change this variable to create a bigger history
                        del self.stack.buf[0]                               # This is where the sliding window happens remove if unnecesary
                    return 'Data Evaluated. Relevant data'
            else:
                return 'Evaluation procedure ended with error code 2\n'
        else:
            return 'Evaluation procedure ended with error code 1\n'


class Simulation:
    def __init__(self):
        self.send_data = False
        self.cp = CommsProtocol(100)

    def on(self):
        self.send_data = True

    def off(self):
        self.send_data = False

    def getRandom(self):
        return randint(5, 10)

    def run_sim(self):
        if self.send_data:
            start_time = time.time()
            for i in range (100):
                print(self.getRandom())
                s = self.cp.evaluate_relevant_data((self.getRandom(), self.getRandom(), self.getRandom()))
            end_time = time.time()
            print(self.cp.stack.buf)

        else:
            print('emitter is off...')

class SimulatedDrone:
    drone = System()
    s = Simulation()
    s.on()
    s.run_sim()

    async def takeoff(self):

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

    async def controlToMakeQuarter(self):

        await asyncio.sleep(5)

        height = True
        if(height):
            print("less than 5m")

            await self.drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, -1.0, 0.0))
            await asyncio.sleep(1)
            height = False
        i = 0
        while(i < self.s.cp.stack.buf.__len__()):
            if self.s.cp.stack.pop_from_stack()[0] > 7:
                print(self.s.cp.stack.pop_from_stack()[0])
                await self.drone.offboard.set_velocity_body(VelocityBodyYawspeed(4.0, 0.0, 0.0, 0.0))
                print("nothing in front")
                await asyncio.sleep(3)
            else:
                await self.drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 30.0))
                print("turn left")
                await asyncio.sleep(3)
            i+=1


        print("-- Stopping offboard")
        try:
            await self.drone.offboard.stop()
        except OffboardError as error:
            print(f"Stopping offboard mode failed with error code: {error._result.result}")


if __name__ == '__main__':
    simulatedDrone = SimulatedDrone()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(simulatedDrone.takeoff())
    loop.run_until_complete(simulatedDrone.controlToMakeQuarter())




