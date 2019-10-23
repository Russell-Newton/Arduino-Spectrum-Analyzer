import numpy as np
import pyaudio

BUFFER_LENGTH = 50
SAMPLE_RATE = 50 * BUFFER_LENGTH
MIN_DB = -50
LOW_FREQUENCY = 0
HIGH_FREQUENCY = 2000
NUM_COLUMNS = 10
BLOCK_STEP = int((HIGH_FREQUENCY - LOW_FREQUENCY) / NUM_COLUMNS)
DATA_STEP = int(SAMPLE_RATE / BUFFER_LENGTH / NUM_COLUMNS)
FREQUENCY_BLOCKS = [c for c in range(LOW_FREQUENCY, HIGH_FREQUENCY, BLOCK_STEP)]


class Generator(object):
    def __init__(self):
        self._sample_data = []
        self._maxes = [0] * NUM_COLUMNS

        p = pyaudio.PyAudio()
        self._stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            output=False,
            frames_per_buffer=BUFFER_LENGTH,
        )

    def update_data(self):
        """


        Note:
            Special thanks to Fábián Tamás László (netom) on GitHub for the base for the Fourier Transform
            See his gist (Simple spectrum analyzer in python using pyaudio and matplotlib):
            https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd

        Returns:
            The newly generated data
        """
        data = []
        try:
            data = np.frombuffer(
                self._stream.read(BUFFER_LENGTH), dtype=np.float32)
            data = np.fft.fft(data)

        except IOError:
            pass
        data = np.log10(np.abs(data) / BUFFER_LENGTH) * 10

        for n in range(0, NUM_COLUMNS):
            data_low = n * DATA_STEP
            data_high = (n + 1) * DATA_STEP
            sub_data = data[data_low: data_high]
            max_f = max(MIN_DB, np.max(sub_data)) - MIN_DB
            self._maxes[n] = max_f
            for i in range(data_low, data_high):
                data[i] = max_f
        self._sample_data = data
        return data

    def get_maxes(self):
        return self._maxes
