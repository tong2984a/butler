import sounddevice as sd
import soundfile as sf
import numpy as np
import openai
import os
import requests
import re
#from colorama import Fore, Style, init
import datetime
import base64
from pydub import AudioSegment
from pydub.playback import play

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

elapikey = open_file('elabapikey.txt')

conversation1 = []  
chatbot1 = open_file('chatbot1.txt')

def text_to_speech(text, voice_id, api_key):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open('output.mp3', 'wb') as f:
            f.write(response.content)
        audio = AudioSegment.from_mp3('output.mp3')
        play(audio)
    else:
        print('Error:', response.text)

voice_id1 = 'Lyl8hhTifO9nwef5pYZ8'

def talk(response):
    #user_message = record_and_transcribe()
    #response = chatgpt(api_key, conversation1, chatbot1, user_message)
    #print_colored("Julie:", f"{response}\n\n")
    user_message_without_generate_image = re.sub(r'(Response:|Narration:|Image: generate_image:.*|)', '', response).strip()
    text_to_speech(user_message_without_generate_image, voice_id1, elapikey)
