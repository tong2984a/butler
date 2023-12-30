import os
import csv
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment

# Initialize the recognizer
r = sr.Recognizer()

# Set up OpenAI API key
client = OpenAI(api_key="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")

# Get the list of .mp4 files in the local folder
folder_path = "mp4_files"
mp4_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]

# Initialize an empty string to store all transcriptions
all_transcriptions = ""

# Loop over the .mp4 files
for mp4_file in mp4_files:
    # Get the path to the .mp4 file
    mp4_path = os.path.join(folder_path, mp4_file)

    # Convert the .mp4 file to .wav
    wav_path = mp4_path.replace(".mp4", ".wav")
    AudioSegment.from_file(mp4_path).export(wav_path, format="wav")

    # Transcribe the .wav file
    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)

    # Add the transcription to the all_transcriptions string
    all_transcriptions += text + " "

    # Delete the .wav file
    os.remove(wav_path)

# Use OpenAI's GPT-3 to generate a description based on the all transcriptions
response = client.completions.create(model="gpt-3.5-turbo-instruct",
    prompt=f"Please provide a brief description for the following text: {all_transcriptions}",
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5)

all_description = response.choices[0].text.strip()

# Open the CSV file for writing
with open("mp4_files/index.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(["file_path", "title", "description"])

    # Loop over the .mp4 files
    for mp4_file in mp4_files:
        # Get the path to the .mp4 file
        mp4_path = os.path.join(folder_path, mp4_file)

        # Convert the .mp4 file to .wav
        wav_path = mp4_path.replace(".mp4", ".wav")
        AudioSegment.from_file(mp4_path).export(wav_path, format="wav")

        # Transcribe the .wav file
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)

        # Use OpenAI's GPT-3 to generate a description based on the all_description
        response = client.completions.create(model="gpt-3.5-turbo-instruct",
            prompt=f"Please provide a brief non-empty description for the following text: {text} using the context of the following description: {all_description}",
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5)

        description = response.choices[0].text.strip()

        # Write a row to the CSV file
        writer.writerow([mp4_path, mp4_file, description])

        # Delete the .wav file
        os.remove(wav_path)