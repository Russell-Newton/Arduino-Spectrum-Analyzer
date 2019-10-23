import serial

from generator import *

CHAR_OFFSET = 21  # Exclamation point


class Sender(object):
    def __init__(self, generator: Generator, port: str = 'COM3'):
        self.generator = generator
        self.ser = serial.Serial(port, 115200, timeout=0.5)
        print("Initializing Sender")
        self.initialize()

    def update(self):
        """
        Updates generator data.
        """
        self.generator.update_data()

    def send(self):
        """
        Sends generator data to the serial. Each height is encoded into a character by adding it to CHAR_OFFSET. This
        provides a valid character for the Arduino serial to process. On the Ardiuno, the CHAR_OFFSET is subtracted
        from the received character's int value.
        """
        send_string = ''
        heights = self.generator.get_mapped_heights()

        # Compress pairs of heights into 1 character.
        for height in heights:
            send_string += chr(height + CHAR_OFFSET)
        self.ser.write(bytes(send_string, 'utf-8'))

    def initialize(self):
        """
        Set up the serial communication with the Arduino. This will ping the Arduino with CHAR_OFFSET. Once the Arduino
        pings back, this will send over pixel map information, offset by CHAR_OFFSET. The Arduino will send a final
        ping, and the init() method will end.
        """

        from_arduino = ""
        while len(from_arduino) is 0:
            self.ser.write(bytes(chr(CHAR_OFFSET), 'utf-8'))    # Ping with CHAR_OFFSET
            from_arduino = str(self.ser.read(), 'utf-8')        # Look for pong

        # Send matrix info
        self.ser.write(bytes("{}{}".format(chr(NUM_COLUMNS), chr(COL_HEIGHT)), 'utf-8'))

        # Wait for pong
        self.ser.timeout = None
        self.ser.read()

    def update_and_send(self):
        self.update()
        self.send()
