import os
from threading import Thread
import cv2

def start_data():
    print("Start data_stream")
    os.system("python get_rawdata.py")

def start_scene():
    print("Start scene_stream")
    os.system("python scene_stream.py")

thread1 = Thread(target = start_data)
thread1.start()
thread3 = Thread(target = start_scene)
thread3.start()