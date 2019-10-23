import numpy as np
import pyaudio

BUFFER_LENGTH = 50
SAMPLE_RATE = 50 * BUFFER_LENGTH  # I grabbed this constant from
MIN_DB = -50  # Low sound cap
LOW_FREQUENCY = 0  # Lowest frequency in stream
HIGH_FREQUENCY = 2000  # Highest frequency in sample
NUM_COLUMNS = 10  # Number of columns to calculate heights for
COL_HEIGHT = 10  # How tall columns are
DATA_STEP = int(SAMPLE_RATE / BUFFER_LENGTH / NUM_COLUMNS)  # Used to cut data into equal parts


class Generator(object):
    """
    A Generator object retrieves an input stream from the default microphone and generates spectrogram data and
    columns for a bar graph-style spectrogram. To create a spectrogram for any computer sounds, make use of VB-Audio
    Cable. Use VB-Audio Output as the default output and make the VB-Audio Input as the default input.

    See Also:
        https://www.vb-audio.com/Cable/
        https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd
        https://www.arduino.cc/reference/en/language/functions/math/map/
    """

    def __init__(self):
        self._sample_data = []
        self._heights = [0] * NUM_COLUMNS  # Setup column heights

        p = pyaudio.PyAudio()  # Setup stream
        self._stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            output=False,
            frames_per_buffer=BUFFER_LENGTH,
        )

    def update_data(self, cap_raw_data: bool = True) -> list:
        """
        Performs a Fast Fourier Transform on the audio stream, converting the results to decibels for the
        frequencies, which gets returned and saved into self._sample_data. The data is then quanitzed into the ranges
        set by FREQUENCY_BLOCKS. The maximum intensity from each range is capped at and then shifted by by MIN_DB,
        so that frequencies at or below MIN_DB are set to 0. These transformed values are saved into the
        corresponding index in self._heights.

        Credit:
            Many thanks to Fábián Tamás László (user netom) on GitHub for his base for the stream Fourier Transform.
            See his gist (Simple spectrum analyzer in python using pyaudio and matplotlib).

        See Also:
            https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd

        Parameters:
            cap_raw_data: Whether or not to set the final data to the appropriate column height.

        Returns:
            The data from the FFT, transformed into decibels.
        """
        data = []
        try:
            data = np.frombuffer(
                self._stream.read(BUFFER_LENGTH), dtype=np.float32)
            data = np.fft.fft(data)
        except IOError:
            pass

        data = np.log10(np.abs(data) / BUFFER_LENGTH) * 10  # Covert to dB

        for n in range(0, NUM_COLUMNS):
            # Cut data into frequency ranges
            data_low = n * DATA_STEP  # Data range low boundary
            data_high = (n + 1) * DATA_STEP  # Data range high boundary
            sub_data = data[data_low: data_high]  # Trim

            # Find max, shift, and save
            max_f = max(MIN_DB, np.max(sub_data)) - MIN_DB
            self._heights[n] = max_f

            # Set all raw data to the appropriate height
            if cap_raw_data:
                for i in range(data_low, data_high):
                    data[i] = max_f
            else: # Shift it, because -dB is dumb
                data -= MIN_DB

        self._sample_data = data
        return data

    def get_heights(self) -> list:
        """
        Returns:
            The column heights calculated by the last call instance of update_data().
        """
        return self._heights

    def get_mapped_heights(self) -> list:
        """
        See Also:
            https://www.arduino.cc/reference/en/language/functions/math/map/

        Returns:
            The column maxes, mapped from [0, -MIN_DB] to [0, COL_HEIGHT]. The mapping function is the same as used for
            Arduinos.
        """

        def _map(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

        return [_map(n, 0, -MIN_DB, 0, COL_HEIGHT) for n in self._heights]
