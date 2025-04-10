import threading
import time

from mic.smartmic import SmartMic
from speaker.speaker import Speaker
from service.youtube import YouTube
from service.chatgpt import GPTClient
from service.smartnews import SmartNews
from cald.smartcal import MyCalendar

class HomeSpeaker(SmartMic, Speaker):
    def __init__(self, chunk=1024, format=None, channels=1, rate=44100,
                 threshold=500, silence_duration=1.0, wake_words=None):
        """
        HomeSpeaker automatically runs SmartMic in the background.
        It monitors for valid audio (i.e. commands following a wake-up word)
        and uses Speaker functionality to play the audio.
        
        Parameters:
        - chunk, channels, rate, threshold, silence_duration: Audio parameters.
        - wake_words: List of wake-up words.
        """
        if format is None:
            import pyaudio
            format = pyaudio.paInt16

        # Initialize SmartMic (which starts microphone monitoring in background).
        SmartMic.__init__(self, chunk=chunk, format=format, channels=channels,
                          rate=rate, threshold=threshold, silence_duration=silence_duration,
                          wake_words=wake_words)
        # Initialize Speaker.
        Speaker.__init__(self, chunk=chunk, format=format, channels=channels, rate=rate)
        
        self.running = True
        # Start a thread to monitor the SmartMic audio queue.
        self.monitor_thread = threading.Thread(target=self._monitor_commands, daemon=True)
        self.monitor_thread.start()
        # Start a thread to ask gpt the question every 1 minute
        #self.gpt_thread = threading.Thread(target=self._routine_gpt_ask, daemon=True)
        #self.gpt_thread.start()
        self.yt = YouTube()
        self.chatgpt = GPTClient()
        self.calendar = MyCalendar()
        print("HomeSpeaker started. Awaiting commands after wake-up word...")

    def _monitor_commands(self):
        """
        Continuously monitor for valid audio from SmartMic.
        When available, convert the command audio to text.
        If text is recognized, use Speaker to speak it.
        If no text is recognized, play the raw audio instead.
        """
        while self.running:
            command_audio = self.get_audio(timeout=1)
            if command_audio is not None:
                command_text = self.convert_audio_to_text(command_audio).lower()
                # if command_text.strip():
                #     print("HomeSpeaker recognized command text:", command_text)
                #     self.play_text(command_text)
                # else:
                #     print("HomeSpeaker received audio but could not convert to text. Playing raw audio.")
                #     self.play_audio(command_audio)
                self.analysis_command(command_text)
            else:
                time.sleep(0.1)

    def stop(self):
        """
        Stop the HomeSpeaker by stopping the monitoring thread,
        then stopping the microphone stream and speaker functionalities.
        The monitor thread is only joined if the current thread is not the monitor thread.
        """
        self.running = False
        import threading
        if self.monitor_thread is not threading.current_thread():
            self.monitor_thread.join()
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'p'):
            self.p.terminate()
        self.calendar.stop_all()
        self.yt.close_video()
        # Call Speaker's stop method to interrupt any TTS or audio playback.
        Speaker.stop(self)
        self.set_talk_session(False)
        print("HomeSpeaker stopped.")

    #Analysis the command text, if the text include "play" word then get the text after "play" word, then call play_vidoe function to play the video. 
    def analysis_command(self, command_text):        
        if "talk to you" in command_text:
            self.set_talk_session(True)
            self.play_text("Hello, I am your home speaker. How can I help you? talk mode is on for 20 minutes")
        if "play" in command_text:
            self.yt.close_video()
            video_name = command_text.split("play")[-1].strip()
            print("Playing video: ", video_name)
            # Call YouTube class to play the video.
            self.yt.play_video(video_name)
        #else if the command text include "stop" or "close" word, then stop the video
        elif "stop" in command_text or "close" in command_text:  
            self.calendar.stop_all()          
            self.interrupt_playback()
            self.yt.close_video()
        elif "news" in command_text:
            topic = command_text #.split("news")[-1].strip()
            print("Searching news for: ", topic)
            self.search_news(topic)
        else:
            self.ask_gpt(command_text)

    def ask_gpt(self, question):
        #call chatgpt class to get the response
        if question and question.strip():
            print("Asking GPT: ", question)
            response = self.chatgpt.ask(question)
            #if response is not empty then play the response
            if response:
                self.play_text(response)
            else:
                #if response is empty then play the command text
                self.play_text("sorry I can not find the answer for your question")

    def search_news(self, topic):
        #call smartnews class to get the news
        news = SmartNews().get_news(topic)
        #if news is not empty then play the news
        if news:
            self.play_text(news)
        else:
            #if news is empty then play the command text
            self.play_text("sorry I can not find the news for your topic")

if __name__ == "__main__":
    try:
        hs = HomeSpeaker()
        print("HomeSpeaker is running. Speak the wake-up word followed by your command.")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Stopping HomeSpeaker...")
    finally:
        hs.stop()
