import os
import threading
from capture_realsense import capture_realsense
from capture_heat_camera import capture_heat_camera
from disk_writer import disk_writer, write_queues
import pyrealsense2 as rs

if __name__ == "__main__":
    # Create directories for saving images
    folders = [
        'depth_images_d435', 'color_images_d435',
        'depth_images_l515', 'heat_images'
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
    realsense_l515_thread = threading.Thread(target=capture_realsense, args=(config_l515, 'l515', 'f1061547'))

    # Initialize disk writer threads for each folder
    writer_threads = [threading.Thread(target=disk_writer, args=(folder,)) for folder in folders]

    # Start threads for heat camera and RealSense cameras
    heat_thread = threading.Thread(target=capture_heat_camera)

    # Start all threads
    for writer_thread in writer_threads:
        writer_thread.start()
    realsense_d435_thread.start()
    realsense_l515_thread.start()
    heat_thread.start()

    # Wait for camera threads to finish
    realsense_d435_thread.join()
    realsense_l515_thread.join()
    heat_thread.join()

    # Signal disk writer threads to terminate
    for folder in folders:
        write_queues[folder].put(None)
    for writer_thread in writer_threads:
        writer_thread.join()
