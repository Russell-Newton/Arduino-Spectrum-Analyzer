import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np
import pyaudio

BUFFER = 50
RATE = 50 * BUFFER
INTERVALS = 20
MIN_DB = -50
LOW = 0
HIGH = RATE
STEPS = 10

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=RATE,
    input=True,
    output=False,
    frames_per_buffer=BUFFER,
)

fig = plt.figure()
line1 = plt.plot([], [])[0]

r = range(0, RATE, int(RATE / BUFFER))
l = len(r)
block_step = int((HIGH - LOW) / STEPS)
data_step = int(RATE / BUFFER / STEPS)
frequency_blocks = [c for c in range(LOW, HIGH, block_step)]


def init_line():
    line1.set_data(r, [0] * l)
    return line1,


def update_line(i):
    data = update_data()
    line1.set_data(r, data)
    return line1,


def update_data():
    try:
        data = np.frombuffer(
            stream.read(BUFFER), dtype=np.float32)
        data = np.fft.fft(data)

    except IOError:
        pass
    data = np.log10(np.abs(data) / BUFFER) * 10

    for n in range(0, STEPS):
        data_low = n * data_step
        data_high = (n + 1) * data_step
        sub_data = data[data_low: data_high]
        max_f = max(MIN_DB, np.max(sub_data)) - MIN_DB
        for i in range(data_low, data_high):
            data[i] = max_f
    return data


plt.xlim(LOW, HIGH)
plt.ylim(0, 60)
plt.xlabel('Frequency')
plt.title('Spectrometer')
plt.grid()

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=0, blit=True
)

plt.show()
