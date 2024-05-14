#!/bin/bash
mkdir ~/.cache/vosk
cd ~/.cache/vosk
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/m>
unzip vosk-model-small-en-us-0.15.zip
sudo apt -y update
sudo apt -y install libasound2-dev
sudo apt -y install portaudio19-dev
sudo apt -y install libunistring-dev libaom-dev libdav1d-dev
sudo apt -y install ffmpeg libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev libpostproc-dev libsdl2-dev libsdl2-2.0-0 libsdl2-mixer-2.0-0 libsdl2-mixer-dev python3-dev
sudo apt -y install vlc
pip3 install simpleaudio
pip3 install vosk
pip3 install sounddevice
pip3 install soundfile
pip3 install opencv-python
pip3 install ffpyplayer
pip3 install ffmpeg-python
pip3 install pydub
pip3 install werkzeug
pip3 install pyaudio
pip3 install colorama
pip3 install RPi.GPIO
pip3 install python-vlc
pip3 install langchain
pip3 install faiss-cpu
pip3 install sentence-transformers
pip3 install streamlit
pip3 install open-interpreter
