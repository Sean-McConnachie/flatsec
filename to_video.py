import os
import sys
import cv2
import datetime as dt

import json
import discord

from VARS import *

class DiscordClient(discord.Client):
    def __init__(self, video_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_path = video_path

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        channel = self.get_channel(DISCORD_RECORDING_CHAN)
        await channel.send(file=discord.File(self.video_path))
        await self.close()
        print("Logged out")
        sys.exit(0)


def upload_to_discord(video_path: str):
    with open(DISCORD_CRED_FP, mode='r') as f:
        creds = json.load(f)
    intents = discord.Intents.default()
    client = DiscordClient(video_path=video_path, intents=intents)
    client.run(creds["token"])
    

def write_video(video_t: int):
    print("Creating video...")
    im_dir = os.path.join(VIDEO_TMP_DIR, str(video_t))
    image_fps = sorted([img for img in os.listdir(im_dir) if img.endswith(".jpg")])

    ofp = os.path.join(VIDEO_DIR, f"{video_t}.mp4")
    shape = cv2.imread(os.path.join(im_dir, image_fps[0])).shape
    video = cv2.VideoWriter(ofp, cv2.VideoWriter_fourcc(*"mp4v"), REC_FPS, (shape[1], shape[0]))
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
    upload_to_discord(ofp)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python to_video.py <video_t>")
        sys.exit(1)
    video_t = int(sys.argv[1])
    write_video(video_t)