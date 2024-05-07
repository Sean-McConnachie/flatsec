import os
import sys
import cv2
import datetime as dt

from VARS import *

def write_video(video_t: int):
    print("Creating video...")
    im_dir = os.path.join(VIDEO_TMP_DIR, str(video_t))
    image_fps = sorted([img for img in os.listdir(im_dir) if img.endswith(".jpg")])

    ofp = os.path.join(VIDEO_DIR, f"{video_t}.avi")
    shape = cv2.imread(os.path.join(im_dir, image_fps[0])).shape
    video = cv2.VideoWriter(ofp, cv2.VideoWriter_fourcc(*"MJPG"), REC_FPS, (shape[1], shape[0]))
    for image in image_fps:
        im_t = int(image.split(".")[0])
        im_tstr = dt.datetime.fromtimestamp(im_t / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")

        im_fp = os.path.join(im_dir, image)
        im_frame = cv2.imread(im_fp)
        cv2.putText(im_frame, im_tstr, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        video.write(im_frame)
        os.remove(im_fp)
    video.release()
    os.rmdir(im_dir)
    print(f"Video created: {ofp}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python to_video.py <video_t>")
        sys.exit(1)
    video_t = int(sys.argv[1])
    write_video(video_t)