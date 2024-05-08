# Top left and bottom right corners of the crop
CROP = ((800, 438), (1140, 764))
# Tune this parameter until you stop getting triggers when nothing is happening (lower = more sensitive)
START_THRESHOLD = 1.5
# Number of seconds to keep before the first bit of motion is detected
LEAD_RECORD_SECONDS = 3
# Number of seconds to keep after the last bit of motion is detected
AFTER_RECORD_SECONDS = 3

# Camera settings
CAM_HEIGHT = 1080
CAM_WIDTH = 1920
CAM_FPS = 30
# 1 = keep every frame, 2 = keep every other frame, 3 = keep every third frame, etc.
RECORD_EVERY = 1
# Of the frames that are being kept, average every n frames
AVERAGE_EVERY = 2
# Discord channel ID to send recordings to
DISCORD_RECORDING_CHAN = 1237290039516467242 

# ====================================
DISCORD_CRED_FP = "discord_creds.json"

IM_DIR = "images"
VIDEO_TMP_DIR = "videos_tmp"
VIDEO_DIR = "videos"

REC_FPS = int(CAM_FPS / RECORD_EVERY)

QUEUE_SIZE = LEAD_RECORD_SECONDS * REC_FPS

FRAME_WIDTH = CROP[1][0] - CROP[0][0]
FRAME_HEIGHT = CROP[1][1] - CROP[0][1]