import json
import os
import warnings

import cv2
import dlib
import torch
from imutils import face_utils
from imutils.video import FileVideoStream
from pyannote.audio import Pipeline
from tqdm import tqdm

from av_speaker_timestamps.timestamp_utils import logger, mouth_aspect_ratio

warnings.filterwarnings("ignore")


class SpeakerTimestamps:
    """
    Initializes the SpeakerTimestamps object.
    Sets up the pipeline for speaker diarization using the pretrained model.
    Determines the device to be used based on GPU availability.
    Loads the necessary shape predictor and detector for face landmark detection.
    Initializes attributes for timestamps, frame count, and frame lists for two speakers.
    """

    def __init__(self):

        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token="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",
        )

        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            dlib.DLIB_USE_CUDA = True
        else:
            self.device = torch.device("cpu")
            dlib.DLIB_USE_CUDA = False

        # TODO: only for debugger. uncomment otherwise
        # os.chdir(os.path.dirname(os.path.realpath(__file__)))

        self.shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.shape_predictor)
        self.times = {}
        self.count_frames = 0
        self.max_speaker0_frames = []
        self.max_speaker1_frames = []

    def diarize(self, audio_file):
        """
        Diarizes the audio file using the pretrained pipeline and saves the diarization results to a file named "diarization.rttm".

        This function first sends the pipeline to the GPU (if available) using the `to` method of the pipeline object.
        Then it applies the pretrained pipeline to the audio file using the `pipeline` method of the pipeline object.
        The diarization results are written to the "diarization.rttm" file using the `write_rttm` method of the `dz` object.

        Parameters:
            None

        Returns:
            None
            :param audio_file: Path to the audio file to diarize
        """
        try:
            # send pipeline to GPU (when available)
            self.pipeline.to(torch.device(self.device))

            # apply pretrained pipeline
            dz = self.pipeline(audio_file)

            with open("diarization.rttm", "w") as rttm:
                dz.write_rttm(rttm)
        except Exception as e:
            logger.error("Unhandled exception in diarize: %s", str(e))
            raise

    def read_diarize_rttm(self):
        """
        Reads the diarization.rttm file and populates the `times` attribute of the class with a list of tuples.
        Each tuple contains the speaker label, a list of start and end times in seconds, and a list of start and end
        frames in the video. The FPS (frames per second) is assumed to be 30.

        Returns:
            None
        """

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
        """
        Initializes the speaker timestamps for the object.

        This function iterates over the `self.times` list and updates the `self.count_frames` attribute with the maximum frame count from all the time intervals. It also updates the `max_speaker0_time` and `max_speaker1_time` variables with the maximum end times for speaker 0 and speaker 1 respectively. Finally, it updates the `self.max_speaker0_frames` and `self.max_speaker1_frames` attributes with the frame intervals for speaker 0 and speaker 1 respectively.

        Parameters:
        - self: The object itself.

        Returns:
        - None
        """

        max_speaker0_time, max_speaker1_time = 0, 0

        count_frames = 0
        for time in self.times:
            if self.count_frames < max(time[2]):
                self.count_frames = max(time[2])

            if time[0] == "SPEAKER_00" and max_speaker0_time < time[1][1]:
                max_speaker0_time = time[1][1]
                self.max_speaker0_frames = time[2]
            elif time[0] == "SPEAKER_01" and max_speaker1_time < time[1][1]:
                max_speaker1_time = time[1][1]
                self.max_speaker1_frames = time[2]

    def open_mouth_detect(self, video):
        """
        Detects open mouth frames in a video and calculates the ratio of open mouth frames for each speaker.

        Args:
            self: The object itself.
            video: The path to the video file to analyze.

        Returns:
            Tuple: A tuple containing the ratio of open mouth frames for speaker 0 and speaker 1.
                   If an exception occurs during the detection process, returns (None, None).
        """

        try:
            MOUTH_AR_THRESH = 0.6
            (mStart, mEnd) = (49, 68)

            fvs = FileVideoStream(path=video).start()
            speaker0_frames_number, speaker1_frames_number = 0, 0

            for current_frame in tqdm(range(self.count_frames)):
                frame = fvs.read()

                if not (
                    self.max_speaker0_frames[0]
                    <= current_frame
                    <= self.max_speaker0_frames[1]
                    or self.max_speaker1_frames[0]
                    <= current_frame
                    <= self.max_speaker1_frames[1]
                ):
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
                        if (
                            self.max_speaker0_frames[0]
                            <= current_frame
                            <= self.max_speaker0_frames[1]
                        ):
                            speaker0_frames_number += 1

                        if (
                            self.max_speaker1_frames[0]
                            <= current_frame
                            <= self.max_speaker1_frames[1]
                        ):
                            speaker1_frames_number += 1

            return (
                speaker0_frames_number
                / (self.max_speaker0_frames[1] - self.max_speaker0_frames[0]),
                speaker1_frames_number
                / (self.max_speaker1_frames[1] - self.max_speaker1_frames[0]),
            )
        except Exception as e:
            logger.exception("Unhandled exception in face detect: %s", str(e))
            return None, None

    def write_timestamps(self, video_file_1, video_file_2, video_1_json, video_2_json):
        """
        Writes the speaker timestamps to JSON files for two video files.

        This function runs the `open_mouth_detect` method to calculate the frequency of speaker 0 and speaker 1
        in each video file. It then determines which speaker is more active based on the frequency values.
        The timestamps for each speaker are extracted from the `times` list and written to separate JSON files.

        Parameters:
            self (SpeakerTimestamps): The instance of the SpeakerTimestamps class.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the writing process.
            :param video_1_json: Path to the JSON file for P1
            :param video_2_json: Path to the JSON file for P2
            :param video_file_1: Path to P1 shot
            :param video_file_2: Path to P2 shot

        """

        # ideally should run the two in parallel process, but causing pc crashes. so have to run linearly.
        video_0_freq0, video_0_freq1 = self.open_mouth_detect(video_file_1)
        video_1_freq0, video_1_freq1 = self.open_mouth_detect(video_file_2)

        try:
            if max(video_0_freq0, video_0_freq1) > max(video_1_freq0, video_1_freq1):
                if video_0_freq0 > video_0_freq1:
                    video_0_speaker = "SPEAKER_00"
                else:
                    video_0_speaker = "SPEAKER_01"
            else:
                if video_1_freq0 > video_1_freq1:
                    video_0_speaker = "SPEAKER_01"
                else:
                    video_0_speaker = "SPEAKER_00"

            video_0_dicts, video_1_dicts = [], []

            video_0_key, video_1_key = 0, 0
            for time in self.times:
                if time[0] == video_0_speaker:
                    video_0_dicts.append(
                        {
                            "Key": video_0_key,
                            "Start": time[1][0],
                            "event": "talking",
                            "End": time[1][0] + time[1][1],
                            "Duration": time[1][1],
                        }
                    )
                    video_0_key += 1

                else:
                    video_1_dicts.append(
                        {
                            "Key": video_1_key,
                            "Start": time[1][0],
                            "event": "talking",
                            "End": time[1][0] + time[1][1],
                            "Duration": time[1][1],
                        }
                    )
                    video_1_key += 1

            with open(video_1_json, "w") as final:
                json.dump(video_0_dicts, final)

            with open(video_2_json, "w") as final:
                json.dump(video_1_dicts, final)

            os.remove("diarization.rttm")
        except Exception as e:
            logger.exception("Unhandled exception in writing timestamps: %s", str(e))
            raise
