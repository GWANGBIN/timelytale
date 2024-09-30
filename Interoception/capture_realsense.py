import pyrealsense2 as rs
import numpy as np
import cv2
import time
from disk_writer import write_queues

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
