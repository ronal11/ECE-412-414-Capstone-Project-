import cv2
import numpy as np
from typing import Tuple, Union, Any

# Dataset file path
COCO_PATH           = '../yolo/coco.names'
CUSTOM_ClASSES_PATH = '../yolo/obj.names'

# Yolo Setup Parameters
MODEL_CFG    = '../yolo/yolo-custom.cfg'
MODEL_WEIGHT = '../yolo/yolo-custom.weights'
MODEL_WIDTH  = 416
MODEL_HEIGHT = 416

# Detection Constants
RESCALE        = 1./255
MEAN           = (0,0,0)
CONF_THRESHOLD = 0.75
NMS_THRESHOLD  = 0.5

# Bounding box sytling constants
BOX_COLOR      = (0,255,0)
BOX_LINE_WIDTH = 2
BOX_FONT       = cv2.FONT_HERSHEY_PLAIN
BOX_FONT_SCALE = 2
BOX_FONT_COLOR = (0,255,0)

def get_class_names(file_path: str) -> list:
    """Opens a text file and returns a list of each line seperated into strings

    Args:
        file_path: File path for a model's supported class names

    Returns:
        class_names: A list of detectable class names
    """

    with open(file_path, 'r') as f:
        class_names = f.read().splitlines()
    return class_names

def cfg_yolo() -> cv2.dnn_Net:
    """Configures OpenCV to use the yoloV4 deep neural network

    Returns:
        net: An OpenCV deep neural network (DNN) object - represents the yoloV4 neural network
    """

    net = cv2.dnn.readNetFromDarknet(MODEL_CFG, MODEL_WEIGHT)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net

def initialize() -> tuple[list, cv2.dnn_Net]:
    """Initializes the YoloV4-tiny-custom model with the Darknet DNN

    Returns:
        class_names: A list of supported objects (classes) that the model can detect
        net: An OpenCV deep neural network (DNN) object that represents the yoloV4 neural network
    """

    class_names = get_class_names(CUSTOM_ClASSES_PATH) # Grab the class names from the desired model
    net = cfg_yolo() # Configure OpenCV to read the YoloV4 model files (cfg and weight)
    return class_names, net

def toggle_camera(cap: cv2.VideoCapture, vid_src: Union[str, int]) -> cv2.VideoCapture | None:
    """Takes in a VideoCapture object and toggles it based on on/off state

    Args:
        cap: An OpenCV VideoCapture object that represents a camera
        vid_src: The integral indicator for a system's webcame to use for video input

    Returns:
        cap: An OpenCV VideoCapture object that represents a camera
    """

    if cap:
        cap.release()
        return None
    else:
        cap = cv2.VideoCapture(vid_src, cv2.CAP_DSHOW)
        return cap

def get_frame(cap: cv2.VideoCapture) -> Tuple[np.ndarray, int, int]:
    """Grabs a single frame of video from the webcame (dictated by "cap")

    Args:
        cap: An OpenCV VideoCapture object that represents a camera

    Returns:
        frame: Current frame of the video input to be processed
        f_width: Width of the frame
        f_height: Height of the frame
    """

    _, frame = cap.read()  # Decode the next frame of video
    f_height, f_width, _ = frame.shape  # Extract the height and width of the image (should be const most frames)
    return frame, f_width, f_height


def get_layer_outputs(frame: np.ndarray, net: cv2.dnn_Net) -> np.ndarray:
    """Computes the detected objects for the current video frame

    Args:
        frame: Current frame of the video input to be processed
        net: An OpenCV deep neural network (DNN) object that represents the yoloV4 neural network

    Returns:
        layer_outputs: A numpy ndarray of detected objects
    """

    # Create a 4D BLOB from the current frames and extract the detected outputs
    blob = cv2.dnn.blobFromImage(frame, RESCALE, (MODEL_WIDTH, MODEL_HEIGHT), MEAN, swapRB=True, crop=False)
    net.setInput(blob)
    output_names = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_names)
    return layer_outputs

def post_processing(layer_outputs: np.ndarray, f_width: int, f_height: int) -> Tuple[list,list,list,list]:
    """Process the outputs from the yolov4 DNN

    Args:
        layer_outputs: A numpy ndarray of detected objects
        f_width: Width of the image being processed
        f_height: Height of the image being processed

    Returns:
        boxes: Top/left coordinates, width, and height for all detected objects (to draw the boxes)
        confidences: Computed confidence value for each detected object
        class_ids: ID related to the class name for each detected object
    """

    # Initialize parameters for bounding boxes
    boxes, b_center_coords, confidences, class_ids = [], [], [], []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]          # Store acting class predictions
            class_id = np.argmax(scores)    # Determine classes with the highest scores
            confidence = scores[class_id]   # Log the confidence of the highest scoring classes

            if confidence > CONF_THRESHOLD:
                center_x = int(detection[0] * f_width)      # Center x-coordinate of detected object
                center_y = int(detection[1] * f_height)     # Center y-coordidnate of detected object
                width    = int(detection[2] * f_width)      # Width of detected object
                height   = int(detection[3] * f_height)     # Height of detected object
                left     = int(center_x - width / 2)        # x-coordinate of the top left conner of the box
                top      = int(center_y - width / 2)        # y-coordinate of the top left corner of the box

                # Append the current object parameters to the list of all detected objects
                boxes.append([left, top, width, height])
                b_center_coords.append([center_x, center_y])
                class_ids.append(class_id)
                confidences.append(float(confidence))
    return boxes, b_center_coords, confidences, class_ids

def process_frame_for_coords(cap, net, class_names) -> Tuple[int, int] | Tuple[None, None]:
    """A processing function that only returns the center coordinates for the first detected object

    Args:
        cap: An OpenCV VideoCapture object that represents a camera
        net: An OpenCV deep neural network (DNN) object that represents the yoloV4 neural network
        class_names: A list of supported objects (classes) that the model can detect

    Returns:
        x_center_coordinate: x-coordindate for the center of the bounding box
        y_center_coordinate: y-coordindate for the center of the bounding box
    """

    if cap:
        frame, f_width, f_height = get_frame(cap)
        layer_outputs            = get_layer_outputs(frame, net)
        boxes, b_center_coords, confidences, class_ids = post_processing(layer_outputs, f_width, f_height)

        if b_center_coords:
            return get_center_coords(b_center_coords, 0)
    return None, None

def draw_bbox(frame: np.ndarray, boxes: list, confidences: list, class_ids: list, class_names: list) -> None:
    """Draw bounding boxes for all detected objects

    Args:
        frame: Current frame of the video input to be processed
        boxes: Box info (top/left coordinates, width, and height) for all boxes to be drawn
        confidences: Confidence values for each box to be drawn
        class_ids: ID number for the name added to each boxe's label
        class_names: All supported classes for the configured model

    Returns:
        None
    """

    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            label = str(class_names[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            cv2.rectangle(frame, (x, y), (x + w, y + h), BOX_COLOR, BOX_LINE_WIDTH)
            cv2.putText(frame, label + " " + confidence, (x, y + 20),
                        BOX_FONT, BOX_FONT_SCALE, BOX_FONT_COLOR, BOX_FONT_SCALE)

def get_center_coords(b_center_coords: list, index: int) -> tuple[Any, Any] | tuple[None, None]:
    """Returns the (x,y) center coordiantes for a desired bounding box

    Args:
        b_center_coords: A collection of center coordinates for all detected objects (current frame)
        index: Index of the object to

    Returns:
        x_center_coordinate: x-coordindate for the center of the bounding box
        y_center_coordinate: y-coordindate for the center of the bounding box
    """
    if b_center_coords[index] is not None:
        return b_center_coords[index][0], b_center_coords[index][1]
    else:
        return None, None