import io
import os

from google.cloud import speech

# Set the Google Cloud credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service_account.json"

client = speech.SpeechClient()

def transcribe_audio(file_path):
    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

# Example usage
transcribe_audio("path/to/your/audio/file.mp3")
