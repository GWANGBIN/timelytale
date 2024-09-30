import cv2
import time
from disk_writer import write_queues

def capture_zed():
    """Captures frames from the ZED camera."""
    cap = cv2.VideoCapture(3)
    if not cap.isOpened():
        print("ZED Camera Open: Failed. Exit program.")
        return

    # Set resolution for ZED camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        start_time = time.time()

        retval, frame = cap.read()
        if not retval:
            print("Failed to grab ZED frame")
            continue

        timestamp = str(int(time.time() * 1000))  # Milliseconds for uniqueness
        write_queues['zed_whole_images'].put((frame, timestamp, 'zed'))

        # Calculate and display the frame rate
        end_time = time.time()
        elapsed_time = end_time - start_time
        frame_rate = 1 / elapsed_time
        print(f"ZED FPS: {frame_rate:.2f}")
