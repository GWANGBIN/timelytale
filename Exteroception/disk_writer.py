import cv2
import queue

# Create queue for saving ZED images
write_queues = {
    'zed_whole_images': queue.Queue()
}

def disk_writer(folder):
    """Continuously writes images from the queue to disk."""
    while True:
        item = write_queues[folder].get()
        if item is None:
            break
        image, timestamp, suffix = item
        cv2.imwrite(f'{folder}/{timestamp}_{suffix}.png', image)
