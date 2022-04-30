import cv
import cv2
import cv_test
import numpy as np

# Dataset file path
COCO_PATH           = '../yolo/coco.names'
CUSTOM_ClASSES_PATH = '../yolo/obj.names'

# Some constant input device/source constants
SYS_WEBCAM = 0
OBS_WEBCAM = 1
DEER1_MP4  = '../videos/deer1.mp4'
DEER2_MP4  = '../videos/deer2.mp4'

def main():
    """
    class_names = cv.get_class_names(CUSTOM_ClASSES_PATH) # Grab the class names from the desired model
    net         = cv.cfg_yolo()                      # Configure OpenCV to read the YoloV4 model files (cfg and weight)
    cv_test.cv_testing_loop_old(SYS_WEBCAM, net, class_names) # Infinite cv loop to continuously read from a video feed
    """

    class_names, net = cv.initialize()
    cap = cv.toggle_camera(None, SYS_WEBCAM)

    cv_test.cv_testing_loop_new(cap, net, class_names)
    # cv_test.cv_testing_coord_processing(cap, net, class_names)

if __name__ == "__main__":
    main()