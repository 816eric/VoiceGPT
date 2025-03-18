import os
import wave
import pyaudio
from audio.recorder import Recorder
from audio.processor import Processor
from gpt.client import GPTClient

def main():
    # Initialize the recorder and GPT client
    recorder = Recorder()    
    gpt_client = GPTClient(api_key="Your API Key")
    processor = Processor()

    print("Recording... Press Ctrl+C to stop.")
    
    try:
        while True:
            # Start recording
            audio_file = recorder.start_recording()

            # Process the recorded audio to extract text
            question = processor.process_audio(audio_file)
            
            # Check for wakeup condition
            if processor.is_wakeup_detected():
                # Send the question to GPT and get the response
                response = gpt_client.send_question(question)
                print("GPT Response:", response)
                processor.speak(response)
            else:
                print("Wakeup word not detected. Please try again.")
            
    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        recorder.stop_recording()

if __name__ == "__main__":
    main()