from generator import *
import serial


class Sender(object):
    def __init__(self, generator: Generator, port: str = 'COM3'):
        self.generator = generator
        self.ser = serial.Serial(port, 115200, rtscts=1)

    def update(self):
        self.generator.update_data()

    def send(self):
        send_string = ''
        heights = self.generator.get_mapped_heights()

        # Compress pairs of heights into 1 character.
        for height1, height2 in zip(heights[0::2], heights[1::2]):
            send_string += chr(16 * int(height1) + int(height2))    # Convert to utf-8
        # print(send_string)
        # send_string += "\r"
        self.ser.write(bytes(send_string))
        pass

    def update_and_send(self):
        self.update()
        self.send()
