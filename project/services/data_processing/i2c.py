from smbus2 import SMBus

class i2cReader:

    def __init__(self, channel, address):
        """
        Init connection to i2c device on specified channel
        :param address: address to read from
        """
        self.bus = SMBus(channel)
        self.address = address

    def read_values(self):
        """
        Read next set of sensor values
        :return: dict containing identifier and sensor value like {x = 20.1, y = 22.1, z = 50.0}
        """

        # Zugriff auf Adresse self.address
        # Zugriff auf bus mit self.bus

        # auslesen von Speicherblock, zusammensetzen

        # erstellen von dict
        # values = {}
        # values[x] = 22.1pi
