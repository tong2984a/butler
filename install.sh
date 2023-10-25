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
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/test_halloween.mp4 
curl https://gist.githubusercontent.com/tong2984a/15805276f9768012c2912af98e7975aa/raw/bf7628a6a733be854b798cf7fb86f6ebae6948de/butler_client.py --output butler_client.py
curl https://gist.githubusercontent.com/tong2984a/6a0fb2280fe5bc8ddaae2036f916a28f/raw/c28b602309e0cdabb794f46f1e4c83075dd51cc3/butler_vosk.py --output butler_vosk.py
cd ~/Desktop
curl https://gist.githubusercontent.com/tong2984a/08feed94ac960d18eb74f2df69813c25/raw/fe17fa24fd3af1f60ea55d55bff1389db39f3a21/demo.sh --output demo.sh
chmod +x demo.sh

