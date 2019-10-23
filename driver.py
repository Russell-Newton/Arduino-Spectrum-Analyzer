from generator import Generator
from sender import Sender

if __name__ == '__main__':
    gen = Generator()
    sender = Sender(gen)
    while True:
        sender.update_and_send()
