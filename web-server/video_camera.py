from threading import Thread, Lock
import cv2, time
import gevent

gevent_active = True

class VideoCamera(object):
    def __init__(self, src=0, fps=1/30, name='VideoCamera'):
        self.capture = cv2.VideoCapture(src, cv2.CAP_ANY)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        # Limit the fps to a maximum of 30 fps
        self.fps = fps
        self.fps_ms = int(self.fps * 1000)

        # Thread to handle capturing frames from the video stream
        self.name = name
        self.lock = Lock()
        self.thread = Thread(name=self.name, target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            with self.lock:
                if self.capture.isOpened():
                    (self.status, self.frame) = self.capture.read()
            if gevent_active:
                gevent.sleep(1/30)
            else:
                time.sleep(1/30)

    def get_frame(self):
        out_frame = None
        with self.lock:
            if self.capture.isOpened():
                if self.frame is not None:
                    out_frame = self.frame
        return out_frame

    def show_frame(self):
        cv2.imshow(self.name, self.frame)
        cv2.waitKey(self.fps_ms)

if __name__ == '__main__':
    t_cam = VideoCamera()

    while True:
        try:
            t_cam.show_frame()
        except AttributeError:
            pass