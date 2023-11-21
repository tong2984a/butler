from moviepy.video.VideoClip import ImageClip
from moviepy.editor import *
import os

def split_up_file():
    path = "./audio/view.mp3"
    audio_clip = AudioFileClip(path)
    n = round(audio_clip.duration)
    counter = 0
    start = 0
    audio_clip.close()
    index = 60

    flag_to_exit = False

    while (True):
        audio_clip = AudioFileClip(path)
        if index >= n:
            flag_to_exit = True
            index = n
        
        temp = audio_clip.subclip(start, index)
        temp_saving_location = f"./audio/temp_audio_folder/temp_{counter}.mp3"
        temp.write_audiofile(filename=temp_saving_location)
        temp.close()
        counter += 1
        start = index
        audio_clip.close()
        if flag_to_exit:
            break
        index += 60

    print('stop')

split_up_file()