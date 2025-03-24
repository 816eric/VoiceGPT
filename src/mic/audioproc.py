import wave
import pyaudio
import numpy as np
import speech_recognition as sr

class AudioProc:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100):
        """
        Provide audio processing features: conversion of audio to text,
        detection of wake-up words, and text-to-speech.
        """
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        
        # Initialize PyAudio instance (for playback/saving).
        self.p = pyaudio.PyAudio()
        
        # Initialize SpeechRecognition and pyttsx3 for text-to-speech.
        self.recognizer = sr.Recognizer()

    def convert_audio_to_text(self, audio_data):
        """
        Convert raw audio bytes to text using Google's Speech Recognition.
        """
        sample_width = self.p.get_sample_size(self.format)
        audio = sr.AudioData(audio_data, self.rate, sample_width)
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            return f"Error: {e}"

    def detect_wakeup_words(self, text, wake_words=None):
        """
        Check if any wake-up word exists in the provided text.
        """
        if wake_words is None:
            wake_words = ["hey gpt", "wake up", "hello"]
        text_lower = text.lower()
        for word in wake_words:
            if word.lower() in text_lower:
                return True
        return False    

    def close(self):
        """
        Terminate the PyAudio session and stop the TTS engine.
        """
        self.p.terminate()
        print("Audio processor closed.")
