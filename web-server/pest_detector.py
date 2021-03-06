import video_camera as vc
import numpy as np
import cv2

from typing import Tuple

# Custom pest detection model
CUSTOM_ClASSES_PATH = 'static/yolo/obj.names'
MODEL_CFG    = 'static/yolo/yolo-custom.cfg'
MODEL_WEIGHT = 'static/yolo/yolo-custom.weights'

# Microsoft COCO Dataset (for testing purposes)
# CUSTOM_ClASSES_PATH = 'static/yolo/coco.names'
# MODEL_CFG    = 'static/yolo/yolov4-tiny.cfg'
# MODEL_WEIGHT = 'static/yolo/yolov4-tiny.weights'

class PestDetector(object):
    def __init__(self, names=CUSTOM_ClASSES_PATH, cfg=MODEL_CFG, weights=MODEL_WEIGHT):
        self.rescale = 1. / 255
        self.mean = (0, 0, 0)
        self.conf_threshold = 0.75
        self.nms_threshold = 0.5

        self.class_names_path = names
        self.cfg_path = cfg
        self.weights_path = weights
        self.model_width = 416
        self.model_height = 416

        self.box_color = (0, 255, 0)
        self.box_line_width = 2
        self.box_font = cv2.FONT_HERSHEY_PLAIN
        self.box_font_scale = 2
        self.box_font_color = (0, 255, 0)

        self.class_names = self.get_class_names()
        self.net = self.cfg_yolo()

        # Limit the fps to a maximum of 30 fps
        self.fps = 1 / 30
        self.fps_ms = int(self.fps * 1000)

        self.cam = vc.VideoCamera(0, self.fps, 'VideoCamera')

    def get_class_names(self) -> list:
        """Opens a text file and returns a list of each line seperated into strings

        Returns:
            class_names: A list of detectable class names
        """

        with open(self.class_names_path, 'r') as f:
            class_names = f.read().splitlines()
        return class_names

    def cfg_yolo(self) -> cv2.dnn_Net:
        """Configures OpenCV to use the yoloV4 deep neural network

        Returns:
            net: An OpenCV deep neural network (DNN) object - represents the yoloV4 neural network
        """
        net = cv2.dnn.readNetFromDarknet(self.cfg_path, self.weights_path)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        return net

    def get_layer_outputs(self, frame) -> np.ndarray:
        """Computes the detected objects for the current video frame

        Args:
            frame: Current frame of the video input to be processed

        Returns:
            layer_outputs: A numpy ndarray of detected objects
        """
        blob = cv2.dnn.blobFromImage(frame, self.rescale, (self.model_width, self.model_width), self.mean,
                                     swapRB=True, crop=False)
        self.net.setInput(blob)
        output_names = self.net.getUnconnectedOutLayersNames()
        layer_outputs = self.net.forward(output_names)
        return layer_outputs

    @staticmethod
    def get_center_coords(b_center_coords, index):
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

    def process_frame(self, frame) -> Tuple[list,list,list,list]:
        """Process the outputs from the yolov4 DNN

        Args:
            frame: Image frame to be processed

        Returns:
            boxes: Top/left coordinates, width, and height for all detected objects (to draw the boxes)
            confidences: Computed confidence value for each detected object
            class_ids: ID related to the class name for each detected object
        """

        f_height, f_width, _ = frame.shape
        layer_outputs = self.get_layer_outputs(frame)

        # Initialize parameters for bounding boxes
        boxes, b_center_coords, confidences, class_ids = [], [], [], []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]          # Store acting class predictions
                class_id = np.argmax(scores)    # Determine classes with the highest scores
                confidence = scores[class_id]   # Log the confidence of the highest scoring classes

                if confidence > self.conf_threshold:
                    center_x = int(detection[0] * f_width)  # Center x-coordinate of detected object
                    center_y = int(detection[1] * f_height) # Center y-coordidnate of detected object
                    width = int(detection[2] * f_width)     # Width of detected object
                    height = int(detection[3] * f_height)   # Height of detected object
                    left = int(center_x - width / 2)        # x-coordinate of the top left conner of the box
                    top = int(center_y - width / 2)         # y-coordinate of the top left corner of the box

                    # Append the current object parameters to the list of all detected objects
                    boxes.append([left, top, width, height])
                    b_center_coords.append([center_x, center_y])
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
        return boxes, b_center_coords, confidences, class_ids

    def process_frame_coords(self, frame) -> Tuple[int, int] | Tuple[None, None]:
        """A processing function that only returns the center coordinates for the first detected object

        Args:
            frame: Image frame to be processed

        Returns:
            x_center_coordinate: x-coordindate for the center of the bounding box
            y_center_coordinate: y-coordindate for the center of the bounding box
        """
        boxes, b_center_coords, confidences, class_ids = self.process_frame(frame)
        if b_center_coords:
            return self.get_center_coords(b_center_coords, 0)
        return None, None

    def draw_bbox(self, frame, boxes, confidences, class_ids):
        """Draw bounding boxes for all detected objects

        Args:
            frame: Current frame of the video input to be processed
            boxes: Box info (top/left coordinates, width, and height) for all boxes to be drawn
            confidences: Confidence values for each box to be drawn
            class_ids: ID number for the name added to each boxe's label

        Returns:
            None
        """

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                label = str(self.class_names[class_ids[i]])
                confidence = str(round(confidences[i], 2))
                cv2.rectangle(frame, (x, y), (x + w, y + h), self.box_color, self.box_line_width)
                cv2.putText(frame, label + " " + confidence, (x, y + 20),
                            self.box_font, self.box_font_scale, self.box_font_color, self.box_font_scale)
        return frame

    def get_frame(self):
        """Returns a single frame from the detector

        Returns
            frame: Processed image frame
        """

        return self.cam.get_frame()

    def show_frame(self, frame):
        """Opens an OpenCV window to show the input frame

        Args:
            frame: Image frame to output to the OpenCV camerra stream window
        """
        cv2.imshow('Video', frame)
        cv2.waitKey(self.fps_ms)