import argparse
import json
import os
import warnings

import cv2
import dlib
import torch
from imutils import face_utils
from imutils.video import FileVideoStream
from pyannote.audio import Pipeline
from scipy.spatial import distance as dist
from tqdm import tqdm

warnings.filterwarnings('ignore')

audio_file = "../assets/Dhruv.wav"
video_file_1 = "../assets/videos/Dhruv.mov"
video_1_file_name = "Dhruv"
video_file_2 = "../assets/videos/Shonu.mov"
video_2_file_name = "Shonu"

os.makedirs("../assets/json/", exist_ok=True)
video_1_json = f"../assets/json/{video_1_file_name}.json"
video_2_json = f"../assets/json/{video_2_file_name}.json"

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="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")

# send pipeline to GPU (when available)
pipeline.to(torch.device("cpu"))

# apply pretrained pipeline
dz = pipeline(audio_file)

with open("diarization.rttm", "w") as rttm:
    dz.write_rttm(rttm)

with open("diarization.rttm") as f:
    file = f.read()

times = file.split("\n")[:-1]
FPS = 30
for i, time in enumerate(times):
    new_time = time.split()[3:5]
    speaker = time.split()[7]
    times[i] = [speaker, [float(new_time[0]), float(new_time[1])]]

for i, time in enumerate(times):
    frame = [int(time[1][0] * FPS), int((time[1][0] + time[1][1]) * FPS)]
    times[i].append(frame)

max_speaker0_time, max_speaker1_time = 0, 0
max_speaker0_frames, max_speaker1_frames = [], []

count_frames = 0
for time in times:
    if count_frames < max(time[2]):
        count_frames = max(time[2])

    if time[0] == 'SPEAKER_00' and max_speaker0_time < time[1][1]:
        max_speaker0_time = time[1][1]
        max_speaker0_frames = time[2]
    elif time[0] == 'SPEAKER_01' and max_speaker1_time < time[1][1]:
        max_speaker1_time = time[1][1]
        max_speaker1_frames = time[2]


def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[9])
    B = dist.euclidean(mouth[4], mouth[7])
    C = dist.euclidean(mouth[0], mouth[6])
    mar = (A + B) / (2.0 * C)
    return mar


def open_mouth(video, count_frames, speaker0_frames, speaker1_frames):
    ap = argparse.ArgumentParser()
    ap.add_argument('-f')
    ap.add_argument("-p", "--shape-predictor",
                    required=False,
                    default='../model/shape_predictor_68_face_landmarks.dat',
                    help="path to facial landmark predictor")
    ap.add_argument("-v", "--video", default=video,
                    help="video path input")
    args = vars(ap.parse_args())

    MOUTH_AR_THRESH = 0.6
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])
    (mStart, mEnd) = (49, 68)

    fvs = FileVideoStream(path=args["video"]).start()
    speaker0_frames_number, speaker1_frames_number = 0, 0
    for current_frame in tqdm(range(count_frames)):
        frame = fvs.read()

        if not (speaker0_frames[0] <= current_frame <= speaker0_frames[1] or
                speaker1_frames[0] <= current_frame <= speaker1_frames[1]):
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            mouth = shape[mStart:mEnd]
            mar = mouth_aspect_ratio(mouth)

            if mar > MOUTH_AR_THRESH:
                if speaker0_frames[0] <= current_frame <= speaker0_frames[1]:
                    speaker0_frames_number += 1

                if speaker1_frames[0] <= current_frame <= speaker1_frames[1]:
                    speaker1_frames_number += 1

    return (speaker0_frames_number / (speaker0_frames[1] - speaker0_frames[0]),
            speaker1_frames_number / (speaker1_frames[1] - speaker1_frames[0]))


# TODO: run on separate threads
video_0_freq0, video_0_freq1 = open_mouth(video_file_1,
                                          count_frames,
                                          max_speaker0_frames,
                                          max_speaker1_frames)

video_1_freq0, video_1_freq1 = open_mouth(video_file_2,
                                          count_frames,
                                          max_speaker0_frames,
                                          max_speaker1_frames)

if max(video_0_freq0, video_0_freq1) > max(video_1_freq0, video_1_freq1):
    if video_0_freq0 > video_0_freq1:
        video_0_speaker = 'SPEAKER_00'
        video_1_speaker = 'SPEAKER_01'

    else:
        video_0_speaker = 'SPEAKER_01'
        video_1_speaker = 'SPEAKER_00'

else:
    if video_1_freq0 > video_1_freq1:
        video_0_speaker = 'SPEAKER_01'
        video_1_speaker = 'SPEAKER_00'

    else:
        video_0_speaker = 'SPEAKER_00'
        video_1_speaker = 'SPEAKER_01'

video_0_dicts, video_1_dicts = [], []

video_0_key, video_1_key = 0, 0
for time in times:
    if time[0] == video_0_speaker:
        video_0_dicts.append({'Key': video_0_key,
                              'Start': time[1][0],
                              'event': 'talking',
                              'End': time[1][0] + time[1][1],
                              'Duration': time[1][1]})
        video_0_key += 1

    else:
        video_1_dicts.append({'Key': video_1_key,
                              'Start': time[1][0],
                              'event': 'talking',
                              'End': time[1][0] + time[1][1],
                              'Duration': time[1][1]})
        video_1_key += 1


with open(video_1_json, "w") as final:
    json.dump(video_0_dicts, final)

with open(video_2_json, "w") as final:
    json.dump(video_1_dicts, final)

os.remove("diarization.rttm")