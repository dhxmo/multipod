import concurrent
import gc
import json
import multiprocessing
import os
import warnings

import psutil
import torch
from pyannote.audio import Pipeline
import argparse

import cv2
import dlib
from imutils import face_utils
from imutils.video import FileVideoStream
from tqdm import tqdm

from timestamp_utils import logger, mouth_aspect_ratio

warnings.filterwarnings('ignore')



audio_file = "../assets/Dhruv.wav"
video_file_1 = "../assets/videos/Dhruv.mov"
video_1_file_name = "Dhruv"
video_file_2 = "../assets/videos/Shonu.mov"
video_2_file_name = "Shonu"

os.makedirs("../assets/json/", exist_ok=True)
video_1_json = f"../assets/json/{video_1_file_name}.json"
video_2_json = f"../assets/json/{video_2_file_name}.json"


class SpeakerTimestamps:
    def __init__(self):

        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token="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")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # TODO: only for debugger. uncomment otherwise
        # os.chdir(os.path.dirname(os.path.realpath(__file__)))

        self.shape_predictor = './model/shape_predictor_68_face_landmarks.dat'
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.shape_predictor)
        self.times = {}
        self.count_frames = 0
        self.max_speaker0_frames = []
        self.max_speaker1_frames = []

    def diarize(self):
        # send pipeline to GPU (when available)
        self.pipeline.to(torch.device(self.device))

        # apply pretrained pipeline
        dz = self.pipeline(audio_file)

        with open("diarization.rttm", "w") as rttm:
            dz.write_rttm(rttm)

    def read_diarize_rttm(self):
        with open("diarization.rttm") as f:
            file = f.read()

        self.times = file.split("\n")[:-1]
        FPS = 30
        for i, time in enumerate(self.times):
            new_time = time.split()[3:5]
            speaker = time.split()[7]
            self.times[i] = [speaker, [float(new_time[0]), float(new_time[1])]]

        for i, time in enumerate(self.times):
            frame = [int(time[1][0] * FPS), int((time[1][0] + time[1][1]) * FPS)]
            self.times[i].append(frame)

    def initialize_speaker_timestamps(self):
        max_speaker0_time, max_speaker1_time = 0, 0

        count_frames = 0
        for time in self.times:
            if self.count_frames < max(time[2]):
                self.count_frames = max(time[2])

            if time[0] == 'SPEAKER_00' and max_speaker0_time < time[1][1]:
                max_speaker0_time = time[1][1]
                self.max_speaker0_frames = time[2]
            elif time[0] == 'SPEAKER_01' and max_speaker1_time < time[1][1]:
                max_speaker1_time = time[1][1]
                self.max_speaker1_frames = time[2]

    def open_mouth_detect(self, video):
        try:
            MOUTH_AR_THRESH = 0.6
            (mStart, mEnd) = (49, 68)

            fvs = FileVideoStream(path=video).start()
            speaker0_frames_number, speaker1_frames_number = 0, 0

            for current_frame in tqdm(range(self.count_frames)):
                frame = fvs.read()

                if not (self.max_speaker0_frames[0] <= current_frame <= self.max_speaker0_frames[1] or
                        self.max_speaker1_frames[0] <= current_frame <= self.max_speaker1_frames[1]):
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # The 0/1 in the second argument indicates that we should (not)/upsample the image
                # 1 time.  This will make everything (same)/bigger and allow us to detect more
                # faces.
                rects = self.detector(gray, 0)

                for rect in rects:
                    shape = self.predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)

                    mouth = shape[mStart:mEnd]
                    mar = mouth_aspect_ratio(mouth)

                    if mar > MOUTH_AR_THRESH:
                        if self.max_speaker0_frames[0] <= current_frame <= self.max_speaker0_frames[1]:
                            speaker0_frames_number += 1

                        if self.max_speaker1_frames[0] <= current_frame <= self.max_speaker1_frames[1]:
                            speaker1_frames_number += 1

            return (speaker0_frames_number / (self.max_speaker0_frames[1] - self.max_speaker0_frames[0]),
                    speaker1_frames_number / (self.max_speaker1_frames[1] - self.max_speaker1_frames[0]))
        except Exception as e:
            logger.exception(e)
            return None, None

    def write_timestamps(self):
        # ideally should run the two in parallel process, but causing pc crashes. so have to run linearly.
        # Define the function to be executed in parallel
        # def process_video(video_file):
        #     print("starting process_video: ", video_file)
        #
        #     video_freq0, video_freq1 = self.open_mouth(video_file)
        #     return video_file, video_freq0, video_freq1
        #
        # # Prepare arguments for the parallel execution
        # args_list = [
        #     video_file_1,
        #     video_file_2
        # ]
        #
        # # Specify the number of threads
        # num_threads = min(10, multiprocessing.cpu_count())
        #
        # # Execute the function in parallel using ThreadPoolExecutor
        # with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        #     future_to_args = {executor.submit(process_video, args): args for args in args_list}
        #
        #     for future in concurrent.futures.as_completed(future_to_args):
        #         print("finished future: ", future.result())
        #
        #         video_file, video_freq0, video_freq1 = future.result()
        #
        #         if video_file == video_file_1:
        #             video_0_freq0, video_0_freq1 = video_freq0, video_freq1
        #         elif video_file == video_file_2:
        #             video_1_freq0, video_1_freq1 = video_freq0, video_freq1

        video_0_freq0, video_0_freq1 = self.open_mouth_detect(video_file_1)
        video_1_freq0, video_1_freq1 = self.open_mouth_detect(video_file_2)

        try:
            if max(video_0_freq0, video_0_freq1) > max(video_1_freq0, video_1_freq1):
                if video_0_freq0 > video_0_freq1:
                    video_0_speaker = 'SPEAKER_00'
                else:
                    video_0_speaker = 'SPEAKER_01'
            else:
                if video_1_freq0 > video_1_freq1:
                    video_0_speaker = 'SPEAKER_01'
                else:
                    video_0_speaker = 'SPEAKER_00'

            video_0_dicts, video_1_dicts = [], []

            video_0_key, video_1_key = 0, 0
            for time in self.times:
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
        except Exception as e:
            logger.exception(e)
            raise


def get_timestamps():
    sts = SpeakerTimestamps()
    sts.diarize()
    sts.read_diarize_rttm()
    sts.initialize_speaker_timestamps()
    sts.write_timestamps()


get_timestamps()
