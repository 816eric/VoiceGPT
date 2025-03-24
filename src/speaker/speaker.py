import threading
import time
import pyaudio
import pyttsx3

class Speaker:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100):
        """
        Initialize the Speaker with parameters for audio playback.
        
        Features:
        - Play text (TTS) and raw audio.
        - Interrupt current playback.
        """
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        
        # Initialize PyAudio for audio playback.
        self.p = pyaudio.PyAudio()
        
        # Thread management.
        self.playback_thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Holds the current TTS engine instance (for interruption).
        self.current_tts_engine = None

    def _play_audio_thread(self, audio_data):
        """
        Internal function to play raw audio data in small chunks.
        Checks periodically for an interrupt signal.
        """
        stream = self.p.open(format=self.format,
                             channels=self.channels,
                             rate=self.rate,
                             output=True)
        # For paInt16, each frame is 2 bytes.
        bytes_per_chunk = self.chunk * 2  
        pos = 0
        while pos < len(audio_data) and not self.stop_event.is_set():
            chunk_data = audio_data[pos: pos + bytes_per_chunk]
            stream.write(chunk_data)
            pos += bytes_per_chunk
        stream.stop_stream()
        stream.close()

    def _play_text_thread(self, text):
        """
        Internal function to convert text to speech and play it.
        A new TTS engine is created for each call to avoid conflicts.
        """
        local_engine = pyttsx3.init()
        self.current_tts_engine = local_engine
        local_engine.say(text)
        local_engine.runAndWait()
        local_engine.stop()
        self.current_tts_engine = None

    def interrupt_playback(self):
        """
        Interrupt only the current audio/TTS playback without shutting down the entire system.
        """
        with self.lock:
            self.stop_event.set()
            if self.current_tts_engine is not None:
                self.current_tts_engine.stop()
            if self.playback_thread is not None and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=0.1)
            self.playback_thread = None

    def play_audio(self, audio_data):
        """
        Play raw audio data. Interrupts any ongoing playback.
        
        Parameters:
        - audio_data: A bytes object containing raw audio.
        """
        self.interrupt_playback()  # Interrupt current playback.
        self.stop_event.clear()
        self.playback_thread = threading.Thread(
            target=self._play_audio_thread, args=(audio_data,), daemon=True
        )
        self.playback_thread.start()

    def play_text(self, text):
        """
        Convert text to speech and play it. Interrupts any ongoing playback.
        
        Parameters:
        - text: The string to be spoken.
        """
        self.interrupt_playback()  # Interrupt current playback.
        self.stop_event.clear()
        self.playback_thread = threading.Thread(
            target=self._play_text_thread, args=(text,), daemon=True
        )
        self.playback_thread.start()

    def stop(self):
        """
        A general stop method that interrupts playback and cleans up audio resources.
        (For systems like HomeSpeaker, use interrupt_playback() to avoid stopping the whole system.)
        """
        self.interrupt_playback()

    def close(self):
        """
        Clean up and terminate audio resources.
        """
        self.interrupt_playback()
        self.p.terminate()



# create a main function to test the Speaker class
def main():
    spkr = Speaker()
    
    print("Playing a long text message...")
    spkr.play_text("This is a long text message that is being spoken. It will be interrupted shortly. Please listen carefully.")
    
    # Wait for 2 seconds before interrupting the current speech.
    time.sleep(3)
    print("Interrupting current speech...")
    spkr.stop()
    
    # Allow a brief pause before resuming.
    time.sleep(2)
    print("Playing a short text message after interruption.")
    spkr.play_text("Speech resumed after interruption.")
    
    # Let the new text finish before closing.
    time.sleep(4)
    spkr.close()

# if __name__ == "__main__":
#     main()

