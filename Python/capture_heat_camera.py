import cv2
import time
from disk_writer import write_queues

def capture_heat_camera():
    """Captures frames from the heat camera."""
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("Heat Camera Open: Failed. Exit program.")
        return

    # Set resolution for the heat camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

    while True:
        start_time = time.time()

        retval, frame = cap.read()
        if not retval:
            print("Failed to grab heat frame")
            continue

        timestamp = str(int(time.time() * 1000))  # Milliseconds for uniqueness
        write_queues['heat_images'].put((frame, timestamp, 'heat'))

        # Calculate and display the frame rate
        end_time = time.time()
        elapsed_time = end_time - start_time
        frame_rate = 1 / elapsed_time if elapsed_time != 0 else float('inf')
        print(f"Heat Camera FPS: {frame_rate:.2f}")
