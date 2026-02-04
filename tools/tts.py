import pyttsx3

def text_to_speech(text, filename="podcast.wav"):
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
