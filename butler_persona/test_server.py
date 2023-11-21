import requests
from gtts import gTTS 
from pydub import AudioSegment
from pydub.playback import play
import butler_vosk

BASE_DOMAIN = "http://3046.jumpingcrab.com:8000"
# Define the specific endpoints.
ENDPOINTS = {
    "video": "/video",
    "ask_llm": "/ask",
    "transcribe_photo": "/transcribe_photo",
    "photo_transcription": "/photo_transcription",
    "photo_transcription_status": "/photo_transcription_status"
}

# Concatenate the base domain and the specific endpoints.
def get_url(endpoint):
  return BASE_DOMAIN + ENDPOINTS[endpoint]

def play_sound(sound_file):
    # Play the sound MP3 audio file
    audio = AudioSegment.from_mp3(sound_file)
    play(audio)

def ask_llm(prompt):
    data = f'Please answer in one short paragraph. {prompt}'
    response = requests.post(get_url("ask_llm"), params={'input': data})

    sample_rate = 8000
    num_channels = 2
    bytes_per_sample = 2

    total = sample_rate * num_channels * bytes_per_sample

    content = response.content.decode('ascii')
    language = 'en'
    myobj = gTTS(text=content, lang=language, slow=False) 
    myobj.save("welcome.mp3")
    play_sound("welcome.mp3")

while True:
    variable = input('Would you like to continue with openAI [y/yes]: ')
    inp = butler_vosk.listen()
    inp = inp.lower()
    print(inp)
    ask_llm(inp)
