#!/bin/bash
mkdir ~/.cache/vosk
cd ~/.cache/vosk
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mkdir ~/work
cd ~/work
sudo apt -y update
sudo apt -y install libasound2-dev
sudo apt -y install portaudio19-dev
sudo apt -y install libunistring-dev libaom-dev libdav1d-dev
sudo apt -y install ffmpeg libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev libpostproc-dev libsdl2-dev libsdl2-2.0-0 libsdl2-mixer-2.0-0 libsdl2-mixer-dev python3-dev
python3 -m venv butler-env
source butler-env/bin/activate
pip3 install simpleaudio
pip3 install vosk
pip3 install sounddevice
pip3 install soundfile
pip3 install opencv-python
pip3 install ffpyplayer
pip3 install ffmpeg-python
pip3 install pydub
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/test_halloween.mp4 
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/butler_client.py
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/butler_vosk.py
cd ~/Desktop
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/demo.sh
chmod +x demo.sh

