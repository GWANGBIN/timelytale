import cv2
import matplotlib.pyplot as plt
from visualizers.Visualizer import Visualizer
import json
import datetime
import time

# cap = cv2.VideoCapture("rtsp://192.168.75.51:8554/live/all")
# cap = cv2.VideoCapture("rtsp://192.168.75.51:24/live/all")
cap = cv2.VideoCapture("rtsp://pi.local:8086/?camera=world")
# cap = cv2.VideoCapture("rtsp://192.168.0.57:8554/live/all")

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

print("재생할 파일 넓이, 높이 : %d, %d"%(width, height))

now = datetime.datetime.now()
print(str(now).replace(':', '').replace('.',''))

fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
out = cv2.VideoWriter('D:/Github/ActionNet/data/tests/eyetracking/' + str(now).replace(':', '').replace('.','') + 'EyetrackingVideo.mp4', fourcc, 30.0, (int(width), int(height)))

while cap.isOpened():
    ret, frame = cap.read()
    # print(ret, frame)

    if ret == False:
        break

    # print(frame.size)

    unixTime = str(time.time())
    currentTime = str(datetime.datetime.now())
    startTime = str(now)
    cv2.putText(frame, startTime, (5,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0))
    cv2.putText(frame, currentTime, (400, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
    cv2.putText(frame, unixTime, (800, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

    # plt.imshow('frame', frame)
    cv2.imshow('rtsp scene stream', frame)
    out.write(frame)
    cv2.waitKey(1)

    k = cv2.waitKey(5) & 0xFF
    if k == ord('e'):
        cv2.destroyWindow('rtsp scene stream')

    else:
        pass
        #print("No Stream opened")

cap.release()
out.release()

