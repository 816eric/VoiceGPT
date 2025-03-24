import threading
import queue
import time
import numpy as np
import pyaudio

class Microphone:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1,
                 rate=44100, threshold=500, silence_duration=1.0):
        """
        Continuously monitor the microphone and record audio when voice is detected.
        Recorded audio is saved to an internal queue.
        """
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.threshold = threshold
        self.silence_duration = silence_duration

        self.audio_queue = queue.Queue()
        self.running = True

        # Initialize PyAudio for input.
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        # Start the monitoring thread.
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def _is_silent(self, data):
        """
        Returns True if the mean absolute amplitude of the audio data is below the threshold.
        """
        audio_data = np.frombuffer(data, dtype=np.int16)
        return np.abs(audio_data).mean() < self.threshold

    def _monitor(self):
        """
        Default monitor: record any audio that is not silent.
        (This method is intended to be overridden in subclasses.)
        """
        while self.running:
            data = self.stream.read(self.chunk)
            if not self._is_silent(data):
                frames = [data]
                silence_time = 0.0
                while self.running:
                    data = self.stream.read(self.chunk)
                    frames.append(data)
                    if self._is_silent(data):
                        silence_time += self.chunk / self.rate
                    else:
                        silence_time = 0.0
                    if silence_time >= self.silence_duration:
                        break
                audio_data = b''.join(frames)
                self.audio_queue.put(audio_data)
            else:
                time.sleep(0.01)

    def get_audio(self, block=True, timeout=None):
        """
        Retrieve the next recorded audio segment from the queue.
        """
        try:
            return self.audio_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        """
        Stop monitoring, close the stream, and terminate PyAudio.
        """
        self.running = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print("Microphone stopped.")
