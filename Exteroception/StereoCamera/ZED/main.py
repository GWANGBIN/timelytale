import os
import threading
from capture_zed import capture_zed
from disk_writer import disk_writer, write_queues

if __name__ == "__main__":
    # Create directory for saving ZED images
    folder = 'zed_whole_images'
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Initialize disk writer thread for ZED images
    writer_thread = threading.Thread(target=disk_writer, args=(folder,))

    # Start thread for ZED camera
    zed_thread = threading.Thread(target=capture_zed)

    # Start the threads
    writer_thread.start()
    zed_thread.start()

    # Wait for ZED camera thread to finish
    zed_thread.join()

    # Signal disk writer thread to terminate
    write_queues[folder].put(None)
    writer_thread.join()
