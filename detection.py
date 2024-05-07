import os
import cv2
import subprocess
import time
import numpy as np
import datetime as dt

from VARS import *

EMPTY_FRAME = np.zeros((FRAME_HEIGHT, FRAME_WIDTH), dtype=np.uint8)

def startup():
    if not os.path.exists(IM_DIR):
        os.mkdir(IM_DIR)
    if not os.path.exists(VIDEO_TMP_DIR):
        os.mkdir(VIDEO_TMP_DIR)
    if not os.path.exists(VIDEO_DIR):
        os.mkdir(VIDEO_DIR)
    for f in os.listdir(IM_DIR):
        os.remove(os.path.join(IM_DIR, f))


class Camera:
    cap: cv2.VideoCapture
    queue_i: int
    queue: list[cv2.Mat]

    recording_i: int
    recording_curr: list[int]

    def __init__(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
        self.cap = cap

        self.queue = [(0, EMPTY_FRAME.copy()) for _ in range(QUEUE_SIZE)]
        self.queue_i = -1

        self.recording_i = -1
        self.recording_curr = None

        self.start = dt.datetime.now()
        self.c = -1
        self.c2 = -1

    def read(self):
        # Camera
        ret, frame = self.cap.read()
        t = int(time.time() * 1000)
        if not ret: return False, False
        self.c += 1

        if self.c % RECORD_EVERY != 0: return True, None

        self.c2 += 1
        EVERY = 10
        if self.c2 % EVERY == 0:
            avg_fps = EVERY / (dt.datetime.now() - self.start).total_seconds()
            self.start = dt.datetime.now()
            print(f"FPS: {avg_fps:.2f}")

        tl = CROP[0]
        br = CROP[1]
        frame = frame[tl[1]:br[1], tl[0]:br[0]]
        
        # Queue
        self.queue_i = (self.queue_i + 1) % QUEUE_SIZE
        self.record_rm_frame(self.queue[self.queue_i][0])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.queue[self.queue_i] = (t, gray)

        # Recording
        self.record_wr_frame(frame, t)  # always write frame
        if self.recording_i > -1: # Currently recording
            self.recording_i -= 1
            self.record_mv_frame(t)
        else:
            self.record_process()

        return True, gray
    
    def release(self):
        self.cap.release()

    def record_start(self):
        if self.recording_i == -1:
            self.recording_curr = int(time.time() * 1000)
            os.mkdir(os.path.join(VIDEO_TMP_DIR, str(self.recording_curr)))
            for f in self.queue:
                self.record_mv_frame(f[0])
        self.recording_i = AFTER_RECORD_SECONDS * REC_FPS

    def record_wr_frame(self, frame, t):
        cv2.imwrite(os.path.join(IM_DIR, f"{t}.jpg"), frame)

    def record_rm_frame(self, prev_t):
        try: os.remove(os.path.join(IM_DIR, f"{prev_t}.jpg"))
        except FileNotFoundError: ...

    def record_mv_frame(self, t):
        if t == 0: return
        try: os.rename(os.path.join(IM_DIR, f"{t}.jpg"), os.path.join(VIDEO_TMP_DIR, str(self.recording_curr), f"{t}.jpg"))
        except FileNotFoundError: ...

    def record_process(self):
        if self.recording_curr is None:
            return
        subprocess.Popen(["python", "to_video.py", str(self.recording_curr)], start_new_session=True)
        self.recording_curr = None


class Average:
    sum = np.array
    frames: list[cv2.Mat]

    def __init__(self, frames: list[cv2.Mat]):
        self.frames = frames
        self.sum = np.zeros(frames[0][1].shape, dtype=np.float32)

    @staticmethod
    def index_of(current: int, dt: int):
        return (current + dt * AVERAGE_EVERY) % QUEUE_SIZE

    def update(self, i, gray):
        self.sum += self.frames[self.index_of(i, -1)][1]
        self.sum -= self.frames[self.index_of(i, -1 - AVERAGE_EVERY)][1]
        average = self.sum / AVERAGE_EVERY
        # normalize to [0, 255]
        average -= np.min(average)
        average /= np.max(average)
        average *= 255
        cv2.imshow("average", average.astype(np.uint8))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            ...
        sq_dist = np.sum((gray - average) ** 2)
        return sq_dist


def main():
    print("Opening camera...")
    cap = Camera()

    print("Starting main loop...")
    avg = Average(cap.queue)
    prev_d = 0
    while True:
        ok, gray = cap.read()
        if not ok: break
        if gray is None: continue
        d = avg.update(cap.queue_i, gray)
        if d > prev_d * START_THRESHOLD:
            print("Motion detected!")
            cap.record_start()
        prev_d = d

if __name__ == "__main__":
    startup()
    main()