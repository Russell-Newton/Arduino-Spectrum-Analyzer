from generator import Generator
from sender import Sender

if __name__ == '__main__':
    gen = Generator()
    sender = Sender(gen)
    while True:
        sender.update_and_send()
        # val = ""
        # for i in range(0, 10):
        #     val += sender._get_valid_from_arduino()
        # print(val)
        # gen.update_data()
        # print(gen.get_mapped_heights())
