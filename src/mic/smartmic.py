import threading
import time
import numpy as np
import pyaudio

import speech_recognition as sr
import pyttsx3

from mic.microphone import Microphone
from mic.audioproc import AudioProc

class SmartMic(Microphone, AudioProc):
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1,
                 rate=44100, threshold=500, silence_duration=1.0, wake_words=None):
        """
        SmartMic monitors the microphone and waits for wake-up words.
        Only after detecting a wake word does it record the subsequent command audio.
        """
        # Initialize the Microphone part.
        Microphone.__init__(self, chunk=chunk, format=format, channels=channels,
                              rate=rate, threshold=threshold, silence_duration=silence_duration)
        # Initialize the AudioProc part.
        AudioProc.__init__(self, chunk=chunk, format=format, channels=channels, rate=rate)
        self.wake_words = wake_words if wake_words is not None else ["hey gpt", "wake up", "hello"]
        self.talk_session_time = 0 #10 * 60  # 10 minutes
                
        # Override the default monitoring thread with our smart monitoring.
        if not hasattr(self, 'thread') or not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self._monitor, daemon=True)
            self.thread.start()
        print("SmartMic started. Listening for wake-up words...")

    def _monitor(self):
        """
        Continuously monitor the microphone. When non-silent audio is detected,
        capture an extended snippet (approx. 1 second) and convert it to text.
        If a wake-up word is found, record the subsequent command (until 1 second of silence)
        and add the command audio to the queue.
        """
        counter = 0
        while self.running:
            counter += 1
            self.talk_session_monitoring(counter)
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
                        print("Stopping recording since silence for 1 second.")
                        break
                    if len(frames) * self.chunk / self.rate >= 20:
                        print("Maximum recording duration of 20 seconds reached, stopping recording.")
                        break
                audio_data = b''.join(frames)
                text = self.convert_audio_to_text(audio_data)                
                if self.detect_wakeup_words(text, self.wake_words) or self.get_talk_session():
                    if not self.get_talk_session():
                        print("Wake-up word detected: ", text)
                    self.audio_queue.put(audio_data)
            else:
                time.sleep(0.01)

    def stop(self):
        """
        Stop monitoring, close the microphone stream, and terminate resources.
        """
        self.running = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.tts_engine.stop()
        print("SmartMic stopped.")

    def set_talk_session(self, session):
        """
        Set the talk session status.
        """
        if session is True:
            self.talk_session_time = 10 * 60  # 10 minutes
            print("Talk session set to:", self.talk_session_time)
        else:
            self.talk_session_time = 0
            print("Talk session ended.")
    
    def get_talk_session(self):
        """
        Get the current talk session status.
        """
        talk_session = False
        #return true if talk_session_time is greater than 0
        if self.talk_session_time > 0:
            talk_session = True
        return talk_session

    def talk_session_monitoring(self, counter):
        #switch talk session to off after 10 minutes if talk session is on  
        if counter % 100 == 0:  #the monitoring is every 10ms, so count 100 times for 1 second 
            if self.talk_session_time > 0:
                self.talk_session_time -= 1
                if self.talk_session_time <= 0:
                    self.set_talk_session(False)
                

# if __name__ == "__main__":
#     try:
#         smart_mic = SmartMic()
#         print("SmartMic is active. Speak the wake-up word followed by your command.")
#         while True:
#             command_audio = smart_mic.get_audio(timeout=1)
#             if command_audio is not None:
#                 print("Received command audio ({} bytes). Converting to text...".format(len(command_audio)))
#                 command_text = smart_mic.convert_audio_to_text(command_audio)
#                 print("Command text:", command_text)
#     except KeyboardInterrupt:
#         print("\nKeyboardInterrupt received. Stopping SmartMic...")
#     finally:
#         smart_mic.stop()
