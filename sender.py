from typing import Callable

import serial

from generator import *

CHAR_OFFSET = 65  # Capital A


class Sender(object):
    """
    A Sender object sends the data from a Generator object to the Arduino with PySerial.
    """

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
            send_string += chr(int(height) + CHAR_OFFSET)
        self.ser.write(bytes(send_string, 'ascii'))

    def initialize(self):
        """
        Set up the serial communication with the Arduino. This will ping the Arduino with CHAR_OFFSET. Once the Arduino
        pings back, this will send over pixel map information, offset by CHAR_OFFSET. The Arduino will send a final
        ping, and the init() method will end.
        """

        self._get_valid_from_arduino("Waiting for hello...")

        def send_metadata():
            self.ser.write(bytes("{}{}{}".format(
                chr(CHAR_OFFSET), chr(NUM_COLUMNS + CHAR_OFFSET), chr(COL_HEIGHT + CHAR_OFFSET)), 'ascii'))

        pong = self._get_valid_from_arduino("Sending metadata...", send_metadata)

        print(pong)
        print(self.ser.read().decode('ascii'))
        print(self.ser.read().decode('ascii'))
        print("Initialized")

    def update_and_send(self):
        self.update()
        self.send()

    def _get_valid_from_arduino(self, debug: str = None, operation: Callable = None) -> str:
        """
        Waits for a valid serial input from the Arduino, printing debug and running operation before checking each
        cycle.

        Returns:
            The value sent by the Arduino.

        """
        pong = ""
        while pong is "":
            if debug is not None:
                print(debug)
            if operation is not None:
                operation()
            pong = self._read_from_arduino()
        return pong

    def _read_from_arduino(self) -> str:
        """
        Attempts to return a valid Serial.write() from the Arduino.
        Returns:
            Either an empty str or the valid serial input from the Arduino.
        """
        from_arduino = ""
        try:
            from_arduino = self.ser.read().decode('ascii')
        except UnicodeDecodeError:
            print("Bad character")
        return from_arduino
