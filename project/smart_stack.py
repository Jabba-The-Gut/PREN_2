from collections import deque
from project.services.const import const
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=const.CONNECTION_STRING))
channel = connection.channel()

channel.exchange_declare(exchange=const.EXCHANGE, exchange_type='topic')


def log(channel, msg):
    print(msg)
    channel.basic_publish(
        exchange=const.EXCHANGE,
        routing_key=const.LOG_BINDING_KEY,
        body=msg
    )


height_margin_offset = 5    # Tweak this value for when we have real time data and offsets
side_margin_offset = 5      # Tweak this value for when we have real time data and offsets
front_margin_offset = 5     # Tweak this value for when we have real time data and offsets


class stack:
    def __init__(self, size):
        self.size = size
        self.buf = deque()

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
            global channel
            log(channel, "[STACK] Nothing to pop from Empty queue")
            return None

class commsProtocol:

    def __init__(self, stack_size):
        self.stack = stack(stack_size)
        self.stack.push_to_stack((0, 0, 0))
        self.min_front_val = 5
        self.min_height = 5
        self.min_side_val = 5
        self.history = 3

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
        global height_margin_offset, side_margin_offset, front_margin_offset
        if isinstance(new_data, tuple):
            if len(new_data) == 3:
                condition_one = ((self.stack.buf[-1][0] + height_margin_offset) or (self.stack.buf[-1][0] - height_margin_offset)) == new_data[0]
                condition_two = ((self.stack.buf[-1][1] + side_margin_offset) or (self.stack.buf[-1][1] - side_margin_offset)) == new_data[1]
                condition_three = ((self.stack.buf[-1][2] + front_margin_offset) or (self.stack.buf[-1][2] - front_margin_offset)) == new_data[2]
                if condition_one or condition_two or condition_three:
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


if __name__ == '__main__':
    cp = commsProtocol(5)
    print(cp.evaluate_relevant_data((30, 55, 55)))
    print(cp.evaluate_relevant_data((30, 60, 55)))
    print(cp.evaluate_relevant_data((30, 80, 55)))
