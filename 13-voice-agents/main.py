# flake8: noqa
import speech_recognition as sr
from graph import graph

# Main function


def main():
    recognizer = sr.Recognizer()    # Initialize recognizer
    microphone = sr.Microphone()  # Initialize microphone

    print("Please say something...")

    # Capture audio from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        recognizer.pause_threshold = 2  # Set pause threshold
        audio = recognizer.listen(source)   # Listen for audio input

    try:
        # Recognize speech using Google Web Speech API
        stt = recognizer.recognize_google(audio)
        print(f"You said: {stt}")
        for event in graph.stream({"messages": [{"role": "user", "content": stt}]}, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()

    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")


main()
