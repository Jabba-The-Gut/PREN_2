import random
from smbus2 import SMBus


class I2cReader:
    """
    This class is responsible for getting the sensor data from the TinyK22
    """

    def __init__(self):
        """
        Init connection to i2c device on address 0x20
        """
        # i2c bus 1
        self.bus = SMBus(1)
        # address TinyK22
        self.address = 0x20

    def read_values(self):
        """
        Read next set of sensor values
        :return: dict containing identifier and sensor value like {front = 201, side = 221, ground = 500, error = 0}.
        """
        sensor_values = {}

        try:
            # Read 6 data bytes from i2c bus
            data = self.bus.read_i2c_block_data(self.address, 0, 6)

            # Rearrange data bytes to 16bit integers
            values = [0, 0, 0, 0]
            values[0] = (data[0] << 8) + data[1]  # distance front
            values[1] = (data[2] << 8) + data[3]  # distance side
            values[2] = (data[4] << 8) + data[5]  # distance ground

            if 0 in values:
                values[3] = 0

            sensor_values["sensor_front"] = values[0]
            sensor_values["sensor_right"] = values[1]
            sensor_values["height"] = values[2]
            sensor_values["error"] = values[3]

            return sensor_values
        except Exception:
            sensor_values["sensor_front"] = 0
            sensor_values["sensor_right"] = 0
            sensor_values["height"] = 0
            sensor_values["error"] = 0

            return sensor_values


