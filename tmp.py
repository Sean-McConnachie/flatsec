import os
import cv2
import numpy as np
import datetime as dt

LEAD_RECORD_SECONDS = 2
AFTER_RECORD_SECONDS = 2

FPS = 30
QUEUE_SIZE = LEAD_RECORD_SECONDS * FPS
HEIGHT = 1080
WIDTH = 1920
EMPTY_FRAME = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
AVERAGE_EVERY = 5

class Camera:
    cap: cv2.VideoCapture
    queue_i: int
    queue: list[cv2.Mat]

    recording_i: int
    recording_wr: cv2.VideoWriter

    def __init__(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS)
        self.cap = cap

        self.queue = [EMPTY_FRAME.copy() for _ in range(QUEUE_SIZE)]
        self.queue_i = -1

        self.recording_i = -1
        self.recording_wr = None

    def read(self):
        # Camera
        ret, frame = self.cap.read()
        if not ret:
            return False
        # timestamp
        now = dt.datetime.now()
        cv2.putText(frame, now.strftime("%Y-%m-%d %H:%M:%S.%f"), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Queue
        self.queue_i = (self.queue_i + 1) % QUEUE_SIZE
        self.queue[self.queue_i] = frame

        # Recording
        if self.recording_i != -1:
            self.recording_wr.write(frame)
            self.recording_i -= 1
        else:
            self.recording_save()
        return True
    
    def release(self):
        self.cap.release()

    def record(self):
        if self.recording_i == -1:
            self.recording_wr = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), FPS, (WIDTH, HEIGHT))
            self.recording_wr.set(cv2.CAP_PROP_FPS, FPS)
            for f in self.queue:
                self.recording_wr.write(f)
        self.recording_i = AFTER_RECORD_SECONDS * FPS

    def recording_save(self):
        if self.recording_wr is None:
            return
        self.recording_wr.release()
        self.recording_wr = None


class Average:
    sum = np.array
    frames: list[cv2.Mat]

    def __init__(self, frames: list[cv2.Mat]):
        self.frames = frames
        self.sum = np.zeros(frames[0].shape, dtype=np.float32)

    @staticmethod
    def index_of(current: int, dt: int):
        return (current + dt * AVERAGE_EVERY) % QUEUE_SIZE

    def update(self, i):
        self.sum += self.frames[self.index_of(i, -1)]
        self.sum -= self.frames[self.index_of(i, -1 - AVERAGE_EVERY)]
        average = self.sum / AVERAGE_EVERY
        # normalize to [0, 255]
        average -= np.min(average)
        average /= np.max(average)
        average *= 255
        cv2.imshow("average", average.astype(np.uint8))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            ...
        sq_dist = np.sum((self.frames[i] - average) ** 2)
        return sq_dist


def main():
    print("Opening camera...")
    cap = Camera()

    print("Starting main loop...")
    avg = Average(cap.queue)
    prev_d = 0
    while cap.read():
        avg.update(cap.queue_i)
        d = avg.update(cap.queue_i)
        if d > prev_d * 1.3:
            print("Motion detected!")
            cap.record()
        prev_d = d


if __name__ == "__main__":
    main()