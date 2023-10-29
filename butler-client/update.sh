#!/bin/bash
cd ~/work
source butler-env/bin/activate
pip3 install ffmpeg-python
pip3 install pydub
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/transcribing.mp3
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/finish_transcription.mp3
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/all_photos_are_transcribed.mp3
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/status_error_missing_photo.mp3
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/status_error_unknown.mp3
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/status_pending.mp3
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/status_ready.mp3
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/butler-client/butler_client.py
cd ~/Desktop
curl -L --retry 20 --retry-delay 2 -O https://github.com/tong2984a/butler/raw/main/demo.sh
chmod +x demo.sh