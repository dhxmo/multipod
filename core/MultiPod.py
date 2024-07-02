from pathlib import Path
from subprocess import call

from av_speaker_timestamps.speaker_timestamps import SpeakerTimestamps
from core.util import logger


class MultiPod:
    def __init__(
        self,
        file_paths,
        video_prefs_selection_var,
        trim_silence_var,
        threshold_scale_value,
        clean_audio_var,
        export_var,
    ):
        self.camera_1_video_path = None
        self.camera_2_video_path = None
        self.camera_3_video_path = None

        for k, v in file_paths.items():
            if v != "No file selected yet.":
                if k == "Shot Angle 1":
                    self.camera_1_video_path = Path(v)
                elif k == "Shot Angle 2":
                    self.camera_2_video_path = Path(v)
                elif k == "Shot Angle 3":
                    self.camera_3_video_path = Path(v)

        self.audio_file = Path(
            "assets/sounds/" + self.camera_1_video_path.stem + ".wav"
        )

        call(
            [
                "ffmpeg",
                "-i",
                self.camera_1_video_path.resolve(),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "44100",
                "-ac",
                "2",
                self.audio_file.resolve(),
            ]
        )

        self.video_1_json = f"assets/json/{self.camera_1_video_path.stem}.json"
        self.video_2_json = f"assets/json/{self.camera_2_video_path.stem}.json"

        self.video_prefs_selection_var = video_prefs_selection_var
        self.trim_silence_var = trim_silence_var
        self.threshold_scale_value = threshold_scale_value
        self.clean_audio_var = clean_audio_var
        self.export_var = export_var

    def run(self, progress_bar, be_patient_label, done_label):
        # Start the progress bar animation
        progress_bar.pack(pady=10)
        progress_bar.start()

        be_patient_label.pack(pady=10)

        #################################################

        try:
            # STEP 2: sync videos with voice diarization. get timestamps
            # TODO: uncomment when ready
            # self.get_speaker_timestamps()

            # STEP 3: if video_prev -> simple cuts -> cut video together simply
            if self.video_prefs_selection_var == "simple_back_and_forth_cuts":
                pass
                # cut video together -> simple back n forth
            elif self.video_prefs_selection_var == "creative_cuts":
                pass
            #      -> cut together with J/L
            #   - If Shot Angle 3 is not none ->  footage available, Cut to a wide angle if more than one person is talking.
            #   - Don’t cut away if someone is monologuing more than 30 secs. Even if they’re briefly interrupted.
            #   - Don’t cut to a new camera for speech less than 3 secs.
            #   - Cut to a new camera 3 secs BEFORE they start speaking. (L-Cut)
            #   - Cut to a new camera 3 secs AFTER they start speaking. (J-Cut)
            #   - Don’t cut to Person D if they talk.
            #

            # STEP 4: if audio_prev -> trim silence -> trim and resync with video
            if self.trim_silence_var:
                pass

            # STEP 5: if audio_prev -> clean audio ->
            # - remove unnecessary words uhh like etc.
            # - make audio very clean and professional.
            # - remove echoes, breath sounds, click pops, etc.
            # resync with video
            if self.clean_audio_var:
                pass

            # STEP 6: if export_prev -> mp4/xml -> export in the correct format
            # for xml ideas -> https://chatgpt.com/c/72f3f96d-341b-495f-b962-7d33bb1d3660
            if self.export_var == "xml":
                pass
            elif self.export_var == "mp4":
                pass

            # STEP 7: delete audio and json files

        except Exception as e:
            logger.exception(e)
            raise
        #################################################

        # After completing the task, update GUI
        progress_bar.stop()
        progress_bar.pack_forget()
        be_patient_label.pack_forget()
        done_label.pack(pady=10)

    def get_speaker_timestamps(self):
        """
        Function to get speaker timestamps by diarizing, reading diarized RTTM file, initializing speaker timestamps, and writing timestamps.
        """
        try:
            sts = SpeakerTimestamps()
            sts.diarize(self.audio_file)
            sts.read_diarize_rttm()
            sts.initialize_speaker_timestamps()
            sts.write_timestamps(
                self.camera_1_video_path,
                self.camera_2_video_path,
                self.video_1_json,
                self.video_2_json,
            )
        except Exception as e:
            logger.exception(e)
            raise
