import cv
import cv2
import numpy as np
from typing import  Union

# Some constant input device/source constants
SYS_WEBCAM = 0
OBS_WEBCAM = 1

def cv_testing_coord_processing(cap: cv2.VideoCapture, net: cv2.dnn_Net, class_names: list) -> None:
    """

    Args:
        cap: An OpenCV VideoCapture object that represents a camera
        net: An OpenCV deep neural network (DNN) object that represents the yoloV4 neural network
        class_names: A list of supported objects (classes) that the model can detect

    Returns:
        None
    """

    while True:
        center_coords = cv.process_frame_for_coords(cap, net, class_names)

        if center_coords[0] is not None:
            print("Center Coords: (x,y) -> (" + str(center_coords[0]) + ", " + str(center_coords[1]) + ")")

        key = cv2.waitKey(1)
        if key == 27:  # ESC -> Exit program
                break
        elif key == 116:  # t -> Toggle the camera
                cap = cv.toggle_camera(cap, SYS_WEBCAM)

    if cap:
        cap.release()

def cv_testing_loop_new(cap: cv2.VideoCapture, net: cv2.dnn_Net, class_names: list) -> None:
    """

    Args:
        cap: An OpenCV VideoCapture object that represents a camera
        net: An OpenCV deep neural network (DNN) object that represents the yoloV4 neural network
        class_names: A list of supported objects (classes) that the model can detect

    Returns:
        None
    """

    while True:
        if cap:
            frame, f_width, f_height = cv.get_frame(cap)
            layer_outputs            = cv.get_layer_outputs(frame, net)
            boxes, b_center_coords, confidences, class_ids = cv.post_processing(layer_outputs, f_width, f_height)

            cv.draw_bbox(frame, boxes, confidences, class_ids, class_names)

            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Uncomment this if output colors are in BGR
            cv2.imshow('Video', frame)

            if b_center_coords:
                x, y = cv.get_center_coords(b_center_coords, 0)
                print("Center Coords: (x,y) -> (" + str(x) + ", " + str(y) + ")")

        key = cv2.waitKey(1)
        if key == 27:  # ESC -> Exit program
            break
        elif key == 116:  # t -> Toggle the camera
            cap = cv.toggle_camera(cap, SYS_WEBCAM)

    if cap:
        cap.release()
    cv2.destroyAllWindows()

def cv_testing_loop_old(vid_src: Union[str, int], net: cv2.dnn_Net, class_names: list) -> None:
    """Main computer vision loop for continously reading and processing a webcam/video feed

    Args:
        vid_src: The integral indicator for a system's webcame to use for video input
        net: OpenCV configured neural network used for detection
        class_names: A list of detectable class names

    Returns:
        None
    """

    # Configure the image capturing device (static images, videos, cameras, etc.)
    cap = cv2.VideoCapture(vid_src)

    while True:
        _, frame = cap.read()               # Decode the next frame of video
        f_height, f_width, _ = frame.shape  # Extract the height and width of the image (should be const most frames)

        layer_outputs = cv.get_layer_outputs(frame, net)
        boxes, b_center_coords, confidences, class_ids = cv.post_processing(layer_outputs, f_width, f_height)
        cv.draw_bbox(frame, boxes, confidences, class_ids, class_names)

        cv2.imshow('Video', frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

    if cap:
        cap.release()
    cv2.destroyAllWindows()
