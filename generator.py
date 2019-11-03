import numpy as np
import pyaudio

BUFFER_LENGTH = 2048
SAMPLE_RATE = 44100
NUM_COLUMNS = 16  # Number of columns to calculate heights for
COL_HEIGHT = 6  # How tall columns are
MAP_IN_MIN = 0.4  # Found through testing


class Generator(object):
    """
    A Generator object retrieves an input stream from the default microphone and generates spectrogram data and
    columns for a bar graph-style spectrogram. To create a spectrogram for any computer sounds, make use of VB-Audio
    Cable. Use VB-Audio Output as the default output and make the VB-Audio Input as the default input.

    See Also:
        https://www.vb-audio.com/Cable/
        https://www.swharden.com/wp/2016-07-31-real-time-audio-monitor-with-pyqt/
        https://www.arduino.cc/reference/en/language/functions/math/map/
    """

    def __init__(self):
        self._sample_data = []
        self._heights = [0] * NUM_COLUMNS  # Setup column heights
        self._frames = []
        self._fft_max = 0

        p = pyaudio.PyAudio()  # Setup stream
        self._stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            output=False,
            frames_per_buffer=BUFFER_LENGTH,
        )

        self._freq_vector = np.fft.rfftfreq(BUFFER_LENGTH, 1. / SAMPLE_RATE)
        self._data_step = int(self._freq_vector[-1] / NUM_COLUMNS)

    def update_data(self):
        """
        Performs a Fast Fourier Transform on the audio stream, converting the results to decibels for the
        frequencies, which gets returned and saved into self._sample_data. The data is then quantized into NUM_COLUMNS
        ranges. The average intensity from each range will be mapped from [0, MAP_IN_MIN] to [0, COL_HEIGHT] and
        returned when get_heights() is called.

        Credit:
            Many thanks to Scott W Harden for the functions that make the FFT work.

        See Also:
            https://www.swharden.com/wp/2016-07-31-real-time-audio-monitor-with-pyqt/
        """
        fft = []
        fftx = []

        try:
            data = np.fromstring(self._stream.read(BUFFER_LENGTH), 'int16')
            fftx, fft = self._getFFT(data)
            fftx *= 2  # Scale so that 400 Hz is actually 400 Hz
            if self._fft_max < np.max(fft):  # Reset the max fft value for normalizing
                self._fft_max = np.max(fft)
            fft /= self._fft_max  # Normalize
        except IOError:
            pass

        fftx_step = fftx[-1] / len(fftx)  # Step distance between points in fftx
        points_in_buffer = BUFFER_LENGTH / fftx_step  # How many points are in the buffer size frequency
        step = int(points_in_buffer / (NUM_COLUMNS - 1))  # How many points should be considered in each column

        # Determine column heights with a segmented average
        for i in range(0, NUM_COLUMNS):
            low = i * step
            high = (i + 1) * step
            self._heights[i] = np.average(fft[low:high])
            for j in range(low, high):
                fft[j] = self._heights[i]

        self._sample_data = fft

    def get_heights(self) -> list:
        """
        Returns:
            The column heights calculated by the last call instance of update_data().
        """
        return self._heights

    def _getFFT(self, data):
        data = data * np.hamming(len(data))
        fft = np.abs(np.fft.fft(data))
        freq = np.fft.fftfreq(len(fft), 1. / SAMPLE_RATE)
        return freq[:int(len(freq) / 2)], fft[:int(len(fft) / 2)]

    def get_mapped_heights(self) -> list:
        """
        See Also:
            https://www.arduino.cc/reference/en/language/functions/math/map/

        Returns:
            The column maxes, mapped from [0, -MIN_DB] to [0, COL_HEIGHT]. The mapping function is the same as used for
            Arduinos.
        """

        def map(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

        return [map(n, 0, MAP_IN_MIN, 0, COL_HEIGHT) for n in self._heights]
