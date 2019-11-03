# Yeah this is pretty much taken right from https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd


import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
from scipy import fftpack

BUFFER = 2048
RATE = 44100
BARS = 16

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

# r = range(0, RATE, int(RATE / BUFFER))
r = fftpack.fftfreq(BUFFER, 1. / RATE)
l = len(r)
data_step = int(RATE / BUFFER / BARS)
time_vect = np.arange(BUFFER, dtype=np.float32) / RATE * 1000
fft_max = 32765


def getFFT(data):
    data = data * np.hamming(len(data))
    fft = np.abs(np.fft.fft(data))
    freq = np.fft.fftfreq(len(fft), 1. / RATE)
    return freq[:int(len(freq) / 2)], fft[:int(len(fft) / 2)]


def init_line():
    line1.set_data(r, [0] * 1)
    return line1,


def update_line(i):
    update_data()
    return line1,


def update_data():
    global fft_max
    try:
        data = np.fromstring(stream.read(BUFFER), 'int16')
        fftx, fft = getFFT(data)
        fftx *= 2
        if fft_max < np.max(fft):
            fft_max = np.max(fft)
        fft /= fft_max

    except IOError:
        pass

    # print(dbfs)
    # print(fft / fft_max)
    fftx_step = fftx[-1] / len(fftx)
    points_in_buffer = BUFFER / fftx_step
    step = int(points_in_buffer / (BARS - 1))
    bars = [0] * len(fft)
    for i in range(0, BARS):
        low = i * step
        high = (i + 1) * step
        height = np.average(fft[low:high])
        for j in range(low, high):
            bars[j] = height

    line1.set_data(fftx, bars)


plt.xlim(0, BUFFER)
plt.ylim(0, 1)
plt.xlabel('Frequency')
plt.title('Spectrometer')
plt.grid()

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=0, blit=True
)

plt.show()
