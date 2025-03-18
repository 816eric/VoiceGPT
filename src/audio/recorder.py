import sounddevice as sd
import numpy as np
import wave

class Recorder:
    def __init__(self, filename='output.wav', samplerate=44100, channels=1, duration=5):
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self.duration = duration
        self.recording = False
        self.frames = []

    def start_recording(self):
        print("Recording...")
        self.audio_data = sd.rec(
            int(self.samplerate * self.duration),
            samplerate=self.samplerate,
            channels=self.channels,
            dtype='int16'
        )
        sd.wait()  # Wait until recording is finished
        self.save_audio(self.filename)
        return self.filename

    def stop_recording(self):
        self.recording = False
        print("Recording stopped.")
        #self.save_audio()

    def save_audio(self, filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 2 bytes per sample (16-bit audio)
            wf.setframerate(self.samplerate)
            wf.writeframes(self.audio_data.tobytes())