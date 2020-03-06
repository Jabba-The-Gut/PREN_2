from collections import deque
import time
'''
Need to add support for thread safe containers using threading.lock().aquire/.release()
'''

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
            # print("Stack is empty cannot pop")
            return None

class commsProtocol:

    def __init__(self, stack_size):
        self.stack = stack(stack_size)
        self.stack.push_to_stack((0, 0, 0))
        self.min_front_val = 5
        self.min_height = 5
        self.min_side_val = 5
        self.history = 3

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


class simulation:
    def __init__(self):
        self.send_data = False
        self.cp = commsProtocol(10)

    def on(self):
        self.send_data = True

    def off(self):
        self.send_data = False


    def run_sim(self):
        if self.send_data:
            start_time = time.time()
            for i in range (5):
                s = self.cp.evaluate_relevant_data((i, i, 3))
                if s.__contains__('Relevant'):
                    print('Pushed : { ( ' ,i ,i, 3, ' ) }')
                else:
                    print('Ignored : { ( ' ,i ,i, 3, ' ) }')

                time.sleep(1.0)
            end_time = time.time()
            print(self.cp.stack.buf)
        else:
            print('emitter is off...')



if __name__ == '__main__':
    s = simulation()
    s.on()
    s.run_sim()