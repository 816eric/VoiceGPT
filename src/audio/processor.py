import speech_recognition as sr
import pyttsx3

class Processor:
    def __init__(self, audio_file=None):
        self.audio_file = audio_file
        self.wakeup = False
        self.wakeup_words = ["hello", "hey", "ok"]
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()
        # Set properties (optional)
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

    # def audio_to_text(self, audio_file):
    #     with open(audio_file, "rb") as audio:
    #         model = whisper.load_model("base")
    #         response = model.transcribe(file=audio)
    #         if response is None or 'text' not in response:
    #             raise ValueError("Transcription failed or 'text' key is missing in the response.")
    #     return response['text']
    
    def audio_to_text(self, audio_file):        
        # Load the audio file
        with sr.AudioFile(audio_file) as source:
            # Record the audio data
            audio_data = self.recognizer.record(source)

            text = ""  # Initialize text with a default value
            try:
                # Recognize the speech using Google Web Speech API
                text = self.recognizer.recognize_google(audio_data)
                print("Text from audio: ", text)                
            except sr.UnknownValueError:
                print("Google Web Speech API could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")
        return text

    def process_audio(self, audio_file):
        text = self.audio_to_text(audio_file)
        self.check_wakeup_text(text)
        return text
    
    def text_to_audio(self, text):        
        # Convert text to speech
        self.engine.say(text)

        # Wait for the speech to finish
        self.engine.runAndWait()

    def speak(self, text):
        self.wakeup = False
        self.text_to_audio(text)

    def check_wakeup_text(self, input_text):
        # """
        # Check if the input text contains any of the configured wakeup words.
        #
        # Args:
        #     input_text (str): The input text to check.
        #     wakeup_words (list): A list of wakeup words to search for.
        #
        # Returns:
        #     bool: True if any wakeup word is found, False otherwise.
        # """
        # Convert input text to lowercase for case-insensitive comparison
        input_text_lower = input_text.lower()
        # Check if any wakeup word is in the input text
        for word in self.wakeup_words:
            if word.lower() in input_text_lower:
                self.wakeup = True # Wakeup word found
                print(f"Wakeup word '{word}' detected!")
                break
            else:
                self.wakeup = False # No wakeup word found        
    
    def is_wakeup_detected(self):
        return self.wakeup  # Return the wakeup status
    
    def wait_for_wakeup(self):
        self.wakeup = False