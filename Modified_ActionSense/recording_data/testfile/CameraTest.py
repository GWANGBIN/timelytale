import cv2

device_indexes = []
for device_index in range(0, 100):
    capture = cv2.VideoCapture(device_index)
    # Try to get a frame to check if the camera exists.
    (success, frame) = capture.read()
    if success:
        device_indexes.append(device_index)
        print("device indexes: ", device_index)
    capture.release()

print(device_indexes)

cap = cv2.VideoCapture(device_indexes[0])
cap1 = cv2.VideoCapture(device_indexes[1])
cap2 = cv2.VideoCapture(device_indexes[2])
cap3 = cv2.VideoCapture(device_indexes[3])

if cap.isOpened():
    if cap1.isOpened():
        if cap2.isOpened():
            if cap3.isOpened():

                while True:
                    status, frame = cap.read()
                    if status:
                        cv2.imshow("camera 1 :", frame)
                    status1, frame1 = cap1.read()
                    if status1:
                        cv2.imshow("camera 2 :", frame1)
                    status2, frame2 = cap2.read()
                    if status2:
                        cv2.imshow("camera 3 :", frame2)
                    status3, frame3 = cap3.read()
                    if status3:
                        cv2.imshow("camera 4 :", frame3)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    fps1 = cap1.get(cv2.CAP_PROP_FPS)
                    fps2 = cap2.get(cv2.CAP_PROP_FPS)
                    fps3 = cap3.get(cv2.CAP_PROP_FPS)
                    print('fps', fps, 'fps2', fps1, 'fps3', fps2, 'fps4', fps3)
                cap.release()
                cv2.destroyWindow()
