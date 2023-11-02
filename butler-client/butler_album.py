import pyaudio
import os
import cv2
import wave
import shutil
import tempfile
import time
import threading
from pydub import AudioSegment
from pydub.playback import play

# Check if the parent folder exists
if not os.path.exists(os.path.join('/media/butler/BLANK', 'media')):
    os.makedirs(os.path.join('/media/butler/BLANK', 'media'))

# Check if the child folder exists
if not os.path.exists(os.path.join('/media/butler/BLANK/media', 'narratives')):
    os.makedirs(os.path.join('/media/butler/BLANK/media', 'narratives'))

def record_audio(output_file):
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 60

    # Create a PyAudio object
    p = pyaudio.PyAudio()

    # Open a stream to record audio
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Record audio for 1 minute
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(1024)
        frames.append(data)

    # Stop the stream and close the PyAudio object
    stream.stop_stream()
    p.terminate()

    # Write the audio data to a WAV file
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.setcomptype('NONE', 'not compressed')
        wf.writeframes(b''.join(frames))

def show_image(image_file):
    # Display the image file
    img = cv2.imread(image_file, cv2.IMREAD_ANYCOLOR)

    # Use high GUI windows
    cv2.startWindowThread()

    # Name the GUI app
    cv2.namedWindow(image_file, cv2.WINDOW_NORMAL)
    cv2.imshow(image_file, img)
    cv2.waitKey(1)

def create_mp3(image_file, output_file):
    # Create an mp3 file corresponding to the jpg file
    os.system(f'ffmpeg -i {image_file} -c:v copy -c:a libmp3lame -q:a 4 {output_file}')

def play_sound(sound_file):
    # Play the sound MP3 audio file
    audio = AudioSegment.from_mp3(sound_file)
    play(audio)

def play_all_photos_and_narratives():
    # Play all the photos and narratives
    for root, dirs, files in os.walk('/media/butler/BLANK/media/narratives'):
        for file in files:
            if file.endswith('.mp3'):
                # Get the corresponding jpg file
                jpg_file = os.path.join('/media/butler/BLANK/media/photos', os.path.basename(root), os.path.splitext(file)[0] + '.jpg')

                # Play the image file and the mp3 file
                show_image(jpg_file)
                play_sound(os.path.join(root, file))
                cv2.destroyWindow(jpg_file)

def next_photo_for_narration():
    # Search for jpg files in the 'photos' folder
    for root, dirs, files in os.walk('/media/butler/BLANK/media/photos'):
        for file in files:
            if file.endswith('.jpg'):
                # Check if a corresponding mp3 file exists
                mp3_file = os.path.join('/media/butler/BLANK/media/narratives', os.path.basename(root), os.path.splitext(file)[0] + '.mp3')
                if not os.path.exists(mp3_file):
                    return os.path.join(root, file), mp3_file
    return None, None

def narrate(photo_file, mp3_file):
    # Play the sound bite MP3 audio file
    show_image(photo_file)

    # Create the child folder if it does not exist
    if not os.path.exists(os.path.dirname(mp3_file)):
        os.makedirs(os.path.dirname(mp3_file))

    # Record audio and create the mp3 file
    with tempfile.NamedTemporaryFile(suffix='.wav') as wav_file:
        # Play the image file and the mp3 file
        record_audio(wav_file.name)
        create_mp3(wav_file.name, mp3_file)
        cv2.destroyWindow(photo_file)

def main():
    continue_narration = True
    intro_sound_bite = "record_first.mp3"

    while (continue_narration):
        photo_file, mp3_file = next_photo_for_narration()
        if mp3_file is None:
            # Play a sound bite MP3 audio file to inform the user before the playback
            play_sound('start_playback.mp3')

            continue_narration = False
            play_all_photos_and_narratives()
            
            # Play a sound bite MP3 audio file to inform the user when all playbacks are complete
            play_sound('end_playback.mp3')
        else:
            # Play the sound bite MP3 audio file
            play_sound(intro_sound_bite)
            intro_sound_bite = "record_next.mp3"
            narrate(photo_file, mp3_file)

if __name__ == '__main__':
    main()
