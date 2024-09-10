import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os
import threading
import queue

# Queues for saving images from different camera sources
write_queues = {
    'depth_images_d435': queue.Queue(),
    'color_images_d435': queue.Queue(),
    'depth_images_l515': queue.Queue(),  # Removed color_images_l515
    'zed_whole_images': queue.Queue(),
    'heat_images': queue.Queue()
}


def disk_writer(folder):
    """Continuously writes images from the queue to disk."""
    while True:
        item = write_queues[folder].get()
        if item is None:
            break
        image, timestamp, suffix = item
        cv2.imwrite(f'{folder}/{timestamp}_{suffix}.png', image)


def capture_realsense(config, camera_name, device_id=None):
    """Captures depth and (optional) color streams from Intel RealSense cameras."""
    pipeline = rs.pipeline()
    if device_id:
        config.enable_device(device_id)
    try:
        pipeline.start(config)
    except Exception as e:
        print(f"Could not start pipeline for {camera_name}. Error: {e}")
        return

    while True:
        start_time = time.time()

        # Retrieve frames from the RealSense camera
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame() if camera_name != 'l515' else None  # No color stream for L515
        if not depth_frame:
            continue

        # Convert depth frames to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_8bit = cv2.convertScaleAbs(depth_image, alpha=0.03)
        timestamp = str(int(time.time() * 1000))  # Milliseconds for uniqueness

        # Add depth images to the queue for saving
        write_queues[f'depth_images_{camera_name}'].put((depth_8bit, timestamp, camera_name))

        # Add color images only if it's not L515
        if color_frame:
            color_image = np.asanyarray(color_frame.get_data())
            write_queues[f'color_images_{camera_name}'].put((color_image, timestamp, camera_name))

        # Calculate and display the frame rate
        end_time = time.time()
        elapsed_time = end_time - start_time
        frame_rate = 1 / elapsed_time if elapsed_time != 0 else float('inf')
        print(f"{camera_name} FPS: {frame_rate:.2f}")


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


if __name__ == "__main__":
    # Create directories for saving images if they don't already exist
    folders = [
        'depth_images_d435', 'color_images_d435',
        'depth_images_l515',  # Removed color_images_l515
        'zed_whole_images', 'heat_images'
    ]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Initialize and configure the Intel RealSense D435 camera
    config_d435 = rs.config()
    config_d435.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config_d435.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    realsense_d435_thread = threading.Thread(target=capture_realsense, args=(config_d435, 'd435', '935422071587'))

    # Initialize and configure the Intel RealSense L515 camera (only depth)
    config_l515 = rs.config()
    config_l515.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
    # Removed color stream configuration for L515
    realsense_l515_thread = threading.Thread(target=capture_realsense, args=(config_l515, 'l515', 'f1061547'))

    # Initialize disk writer threads for each folder
    writer_threads = [threading.Thread(target=disk_writer, args=(folder,)) for folder in folders]

    # Start threads for ZED and heat cameras
    zed_thread = threading.Thread(target=capture_zed)
    heat_thread = threading.Thread(target=capture_heat_camera)

    # Start all threads
    for writer_thread in writer_threads:
        writer_thread.start()
    realsense_d435_thread.start()
    realsense_l515_thread.start()
    zed_thread.start()
    heat_thread.start()

    # Wait for camera threads to finish
    realsense_d435_thread.join()
    realsense_l515_thread.join()
    zed_thread.join()
    heat_thread.join()

    # Signal disk writer threads to terminate
    for folder in folders:
        write_queues[folder].put(None)
    for writer_thread in writer_threads:
        writer_thread.join()
