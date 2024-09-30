import cv2
import queue

# Create queues for saving images from different camera sources
write_queues = {
    'depth_images_d435': queue.Queue(),
    'color_images_d435': queue.Queue(),
    'depth_images_l515': queue.Queue(),
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
