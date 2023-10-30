import logging
import cv2
import numpy as np
import time
from pydub import AudioSegment
from pydub.playback import play
import requests
import sounddevice as sd
import soundfile as sf
import simpleaudio
import butler_vosk
import os
import pathlib
import subprocess
import ffmpeg
from ffpyplayer.player import MediaPlayer
from werkzeug.utils import secure_filename

TEMP_FILE = "output.mp4"
BASE_DOMAIN = "http://3046.jumpingcrab.com:5000"
# Define the specific endpoints.
ENDPOINTS = {
    "video": "/video",
    "ask_llm": "/ask_llm",
    "transcribe_photo": "/transcribe_photo",
    "photo_transcription": "/photo_transcription",
    "photo_transcription_status": "/photo_transcription_status"
}
PHOTOS_FOLDER = pathlib.Path("/media/butler/BLANK/media/photos")
PHOTOS_TMP_FOLDER = PHOTOS_FOLDER.joinpath("tmp").resolve()
PHOTOS_TRANSCRIPTION_FOLDER = PHOTOS_FOLDER.joinpath("transcription").resolve()

# Concatenate the base domain and the specific endpoints.
def get_url(endpoint):
  return BASE_DOMAIN + ENDPOINTS[endpoint]

def narrativePhoto(imageFile, audioFile, outputFile):
    print("narra")
    cmd = "ffmpeg -loop 1 -i % s -i % s -vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' -c:v libx264 -c:a copy -shortest % s" % (imageFile, audioFile, outputFile)
    subprocess.call(cmd, shell=True)

def saveVideo(videoFile, outputFile):
    response = requests.get(get_url("video"), data=videoFile)
    if response.status_code == 200:
        with open(outputFile, 'wb') as f:
            f.write(response.content)
    else:
        print('Error:', response.text)

def ffmpegVideo(file):
    video=cv2.VideoCapture(file)
    player = MediaPlayer(file)
    start_time = time.time()
    while video.isOpened():
        ret, frame=video.read()
        audio_frame, val = player.get_frame()
        if not ret:
            print("End of video")
            break
        if cv2.waitKey(1) == ord("q"):
            break
        cv2.imshow("Video", frame)
        if val != 'eof' and audio_frame is not None:
            img, t = audio_frame
        elapsed = (time.time() - start_time) * 1000  # msec
        play_time = int(video.get(cv2.CAP_PROP_POS_MSEC))
        sleep = max(1, int(play_time - elapsed))
        if cv2.waitKey(sleep) & 0xFF == ord("q"):
            break
    player.close_player()
    video.release()
    cv2.destroyAllWindows()

def ask_llm(prompt):
    data = f'Please answer in one short paragraph. {prompt}'
    response = requests.get(get_url("ask_llm"), data=data, headers={'Content-Type': 'text/plain'})

    sample_rate = 8000
    num_channels = 2
    bytes_per_sample = 2

    total = sample_rate * num_channels * bytes_per_sample

    logging.basicConfig(level=logging.INFO)

    content = response.content

    # Just to ensure that the file does not have extra bytes
    blocks = len(content) // total
    content = content[:total * blocks]

    wave = simpleaudio.WaveObject(audio_data=content,
                                sample_rate=sample_rate,
                                num_channels=num_channels,
                                bytes_per_sample=bytes_per_sample)
    control = wave.play()
    control.wait_done()

def search_for_tmp_files(tmp_folder, photos_folder, transcription_folder):
  # Search for .tmp files in the 'pending' folder.
  for file in os.listdir(tmp_folder):
    secured_file = secure_filename(file)
    if secured_file != file:
        os.rename(file, secured_file)
    if secured_file.endswith(".tmp"):
      return secured_file.replace(".tmp", ".jpg")

  # If no .tmp files are found in the 'pending' folder, search for .jpg files in the 'photos' folder.
  for file in os.listdir(photos_folder):
    if file.endswith(".jpg"):
      secured_file = secure_filename(file)
      if secured_file != file:
          photo_file = os.path.join(photos_folder, file)
          rename_to = os.path.join(photos_folder, secured_file)
          os.rename(photo_file, rename_to)
      # Look for a corresponding .txt file in the 'description' folder.
      mp4_file = os.path.join(transcription_folder, secured_file.replace(".jpg", ".mp4"))
      if not os.path.exists(mp4_file):
        # Create a corresponding .tmp file in the 'pending' folder.
        tmp_file = os.path.join(tmp_folder, secured_file.replace(".jpg", ".tmp"))
        with open(tmp_file, "w") as f:
          f.write("")
        return secured_file

  # If all files are processed, return None.
  return None

while True:
    inp = butler_vosk.listen()
    inp = inp.lower()
    print(inp)
    if all([x in inp for x in ['hey', 'brian']]):
        ask_llm(inp)
        break
    if all([x in inp for x in ['quit']]):
        break
    if all([x in inp for x in ['photo', 'transcription', 'status']]):
        filename = search_for_tmp_files(PHOTOS_TMP_FOLDER, PHOTOS_FOLDER, PHOTOS_TRANSCRIPTION_FOLDER)
        r = requests.get(get_url("photo_transcription_status"), params={"filename": filename})
        if r.json()["status_ready"]:
            print("Transcription is ready.")
            audio = AudioSegment.from_mp3('status_ready.mp3')
            play(audio)
        elif r.json()["status_pending"]:
            print("Photo is being transcribed.")
            audio = AudioSegment.from_mp3('status_pending.mp3')
            play(audio)
        elif r.json()["status_has_photo"]:
            print("Error - Photo exists. Status is unknown.")
            audio = AudioSegment.from_mp3('status_error_unknown.mp3')
            play(audio)
        else:
            print("Error - Photo does not exist.")
            audio = AudioSegment.from_mp3('status_error_missing_photo.mp3')
            play(audio)
        break
    if all([x in inp for x in ['next', 'photo', 'transcription']]):
        filename = search_for_tmp_files(PHOTOS_TMP_FOLDER, PHOTOS_FOLDER, PHOTOS_TRANSCRIPTION_FOLDER)
        photo_file = os.path.join(PHOTOS_FOLDER, filename)
        r = requests.get(get_url("photo_transcription"), params={"filename": filename})
        if r.status_code == 200:
            # The request was successful
            print("Please wait. System processing.")
            wav_file = os.path.join(PHOTOS_TRANSCRIPTION_FOLDER, filename.replace(".jpg", ".wav"))
            with open(wav_file, 'wb') as f:
                f.write(r.content)

            mp3_file = os.path.join(PHOTOS_TRANSCRIPTION_FOLDER, filename.replace(".jpg", ".mp3"))
            ffmpeg = ffmpeg.input(wav_file).output(mp3_file)
            ffmpeg.run()

            video_file = os.path.join(PHOTOS_TRANSCRIPTION_FOLDER, filename.replace(".jpg", ".mp4"))
            narrativePhoto(photo_file, mp3_file, video_file)
            tmp_file = os.path.join(PHOTOS_TMP_FOLDER, filename.replace(".jpg", ".tmp"))
            os.remove(tmp_file)
            ffmpegVideo(video_file)
        else:
            # The request failed
            print("The request failed with status code {}".format(r.status_code))
            print("Try to transcribe next photo")
        break
    if all([x in inp for x in ['next', 'transcribe', 'photo']]):
        filename = search_for_tmp_files(PHOTOS_TMP_FOLDER, PHOTOS_FOLDER, PHOTOS_TRANSCRIPTION_FOLDER)
        photo_file = os.path.join(PHOTOS_FOLDER, filename)
        if filename is None:
            print("All photos are transcribed successfully.")
            audio = AudioSegment.from_mp3('all_photos_are_transcribed.mp3')
            play(audio)
        elif os.path.isfile(photo_file):
            audio = AudioSegment.from_mp3('transcribing.mp3')
            play(audio)
            upload_file = open(photo_file, "rb")
            r = requests.post(get_url("transcribe_photo"), files = {"photo file": upload_file})
            print(r.text)
            audio = AudioSegment.from_mp3('finish_transcription.mp3')
            play(audio)
        break
    if all([x in inp for x in ['photo', 'restaurant']]):
        saveVideo("larry_01.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['photo', 'young']]):
        saveVideo("larry_02.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['photo', 'customers']]):
        saveVideo("larry_03.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['photo', 'growing', 'up']]):
        saveVideo("larry_04.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['photo', 'city', 'lights']]):
        saveVideo("larry_05.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['photo', 'duck']]):
        saveVideo("larry_06.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['photo', 'larry']]):
        saveVideo("larry_07.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['talk', 'larry']]):
        saveVideo("larry_intro.mp4", TEMP_FILE)
        ffmpegVideo(TEMP_FILE)
        break
    if all([x in inp for x in ['test', 'halloween']]):
        ffmpegVideo("test_halloween.mp4")
        break
