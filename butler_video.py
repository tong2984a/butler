#!/usr/bin/env python3

import time
import vlc

def vlcVideo(file):
    player = vlc.MediaPlayer(file)
    player.play()
    time.sleep(1.5)
    duration = player.get_length() / 1000
    print(duration)
    time.sleep(duration)

def play(filename):
    vlcVideo(filename)
