class RingBuffer:
    """
    Simple ring buffer
    """

    def __init__(self, size):
        self.data = [0 for i in range(size)]

    def append(self, x):
        """
        Append the specified element to the buffer and remove the element at index 0
        :param x: Element to append
        :return: None
        """
        self.data.pop(0)
        self.data.append(x)

    def get(self):
        """
        Get the content from the ringbuffer
        :return: list containing buffer elements
        """
        return self.data
