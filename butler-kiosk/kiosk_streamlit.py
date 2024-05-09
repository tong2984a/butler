import faiss
import pickle
import json
import streamlit as st

from colorama import Fore, Back, Style
import os
import platform
import time
import sounddevice as sd
import soundfile as sf
import vlc
import requests
import RPi.GPIO as GPIO

import logging
import cv2
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio
import pathlib
import subprocess
import ffmpeg
from ffpyplayer.player import MediaPlayer
from werkzeug.utils import secure_filename

import butler_vosk


GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

index = faiss.read_index("training.index")

with open("faiss.pkl", "rb") as f:
    store = pickle.load(f)

store.index = index

def clear_screen():
    if platform.system() == 'Windows':
        os.system("cls")
    else:
        os.system("clear")

def splash_screen(text=""):
    print(Fore.WHITE + """這個機器,用來保存人類對生命的渴望和希冀""" + Style.RESET_ALL)
    print(Fore.MAGENTA + """
   @@@%                                                             +@@@                                                                              
   @@@%                                                             +@@@                                                                              
   @@@%                                                             +@@@                                                                              
   @@@%                                                             +@@@                                                                              
   @@@%                                                             +@@@                                                                              
   @@@%           =@@@@@@@    @@@ @@@@ +@@=@@@@*@@@     @@@#        +@@@            @@@@@@@:                                                          
   @@@%           @@@@@@@@@   @@@@@@@@ +@@@@@@@ @@@     @@@         +@@@           @@@@@@@@@                                                          
   @@@%          @@@:   @@@   @@@@@:@  +@@@@-%# @@@#   :@@@         +@@@          %@@@   @@@%                                                         
   @@@%           .@    @@@   @@@@     +@@@      @@@   @@@.         +@@@            +    *@@@                                                         
   @@@%                @@@@   @@@@     +@@@      @@@   @@@          +@@@                *@@@@                                                         
   @@@%            @@@@@@@@   @@@@     +@@@      @@@% :@@@          +@@@            %@@@@@@@@                                                         
   @@@%          @@@@@@@@@@   @@@@     +@@@       @@@ @@@           +@@@           @@@@@@@@@@                                                         
   @@@%          @@@    @@@   @@@%     +@@@       @@@ @@@           +@@@          @@@@   *@@@                                                         
   @@@%         :@@@    @@@   @@@%     +@@@       -@@@@@@           +@@@          @@@    @@@@                                                         
   @@@@@@@@@@@@  @@@   @@@@   @@@%     +@@@        @@@@@            +@@@@@@@@@@@  @@@@  #@@@@                                                         
   @@@@@@@@@@@@  @@@@@@@@@@.  @@@%     +@@@        @@@@@            +@@@@@@@@@@@  @@@@@@@@@@@                                                         
   @@@@@@@@@@@@   @@@@@  @@@  @@@%     +@@@         @@@-            +@@@@@@@@@@@   @@@@@% @@@                                                         
                                                    @@@                                                                                               
                                                   @@@@                                                                                               
                                                @@@@@@                                                                                                
                                                @@@@@@                                                                                                
                                                @@@@                                                                                                  
    """ + Style.RESET_ALL)

    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    for i, char in enumerate(text):
        print(colors[i % len(colors)] + char, end="", flush=True)
        time.sleep(0.05)
    print(Style.RESET_ALL)

def vlcVideo(file):
    vlc_instance = vlc.Instance('--no-xlib -q > /dev/null 2>&1')
    player = vlc_instance.media_player_new(file)
    player.set_fullscreen(True)
    player.play()
    time.sleep(1.5)
    duration = player.get_length() / 1000
    time.sleep(duration)
    player.stop()

def runPrompt():
    def onMessage(question):
        docs_and_scores = store.similarity_search_with_score(question, k=1)
        for i, doc in enumerate(docs_and_scores):
            print("page content:", doc[0].page_content, "score:", doc[1])
            json_object = json.loads(doc[0].page_content)
            print("file:", json_object['File'])

    while True:
        question = input("Ask a question > ")
        answer = onMessage(question)
        print(f"Bot: {answer}")

st.info('Sample Prompt 1 : What are the most rewarding aspects of your journey in the restaurant business that you hold close to your heart?')
st.info('Sample Prompt 2 : Could you provide some background on your upbringing and the place that shaped you into the person you are today?')
st.info('Sample Prompt 3 : Tell us about yourself.') 
st.info("Sample Prompt 4 : Tell me about Larry La's journey in the restaurant business.")


splash_screen()
while True:
    inp = "default"
    filename = 'myrecording.wav'
    #is_pressed = GPIO.input(4)
    is_pressed = True
    try:
        if is_pressed:
            inp = butler_vosk.listen()
            inp = inp.lower()
            user_input = (json.loads(inp))["text"]
            print(user_input)

            st.chat_message("user").write(user_input)
            with st.chat_message("assistant"):
                docs_and_scores = store.similarity_search_with_score(user_input, k=1)
                for i, doc in enumerate(docs_and_scores):
                    print("page content:", doc[0].page_content, "score:", doc[1])
                    json_object = json.loads(doc[0].page_content)
                    mp4 = json_object['File']
                    print("mp4:", mp4)
                    subfolder = "mp4_files"
                    file_path = os.path.join(subfolder, mp4)
                    video_file = open(file_path, 'rb') #enter the filename with filepath
                    video_bytes = video_file.read() #reading the file
                    st.video(video_bytes) #displaying the video

    except Exception as e:
        print(e)
        print('error - internet connection failed')
