from pathlib import Path
from subprocess import call

from av_speaker_timestamps.speaker_timestamps import SpeakerTimestamps
from core.Timestamps import Timestamps, mod_json_2_specs
from core.util import logger


class MultiPod(object):
    def __init__(
        self,
        file_paths,
        video_prefs_selection_var,
        trim_silence_var,
        threshold_scale_value,
        clean_audio_var,
        export_var,
    ):
        """
        Initializes the MultiPod object with the provided parameters.

        Parameters:
            file_paths (dict): A dictionary containing file paths for different shot angles.
            video_prefs_selection_var (str): The selected video preference.
            trim_silence_var (bool): Boolean flag for trimming silence.
            threshold_scale_value (float): The threshold scale value.
            clean_audio_var (bool): Boolean flag for cleaning audio.
            export_var (str): The selected export format.

        Returns:
            None
        """
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

        # TODO: overwrite if already present
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

        self.filename_1 = self.camera_1_video_path.stem
        self.filename_2 = self.camera_2_video_path.stem
        self.filename_3 = self.camera_3_video_path.stem

        self.video_1_json = f"assets/json/{self.filename_1}.json"
        self.video_2_json = f"assets/json/{self.filename_2}.json"

        self.video_1_json_mod = f"assets/json/{self.filename_1}_mod.json"
        self.video_2_json_mod = f"assets/json/{self.filename_2}_mod.json"

        self.combined_json = "assets/json/combined_timestamps.json"

        self.mts = Timestamps(self.combined_json)

        self.video_prefs_selection_var = video_prefs_selection_var
        self.trim_silence_var = trim_silence_var
        self.threshold_scale_value = threshold_scale_value
        self.clean_audio_var = clean_audio_var
        self.export_var = export_var

    def run(self, progress_bar, be_patient_label, done_label):
        """
        Runs the entire multipod processing workflow including syncing videos with voice diarization, making cuts
        based on video preferences, trimming silence and cleaning audio if needed, and exporting the final output.

        Parameters:
            progress_bar: The progress bar widget to show the progress of the workflow.
            be_patient_label: The label widget indicating to be patient during the processing.
            done_label: The label widget indicating the completion of the processing.

        Returns:
            None
        """

        # Start the progress bar animation
        progress_bar.pack(pady=10)
        progress_bar.start()

        be_patient_label.pack(pady=10)

        #################################################

        try:
            # STEP 2: sync videos with voice diarization. get timestamps
            # self.get_speaker_timestamps()

            # STEP 3a -> preprocess the json
            self.preprocess_json()

            # STEP 3b: if video_prev -> simple cuts -> cut video together simply
            # TODO: when silent and P3 provided, use that, else pick P1/P2 randomly

            if self.video_prefs_selection_var == "simple_back_and_forth_cuts":
                pass
                # cut video together -> simple back n forth
            elif self.video_prefs_selection_var == "creative_cuts":
                pass
                #   - If P3 is not none -> Cut to a wide angle if both are talking.
                #   - Don’t cut away if someone is monologuing more than 30 secs. Even if they’re briefly interrupted.
                #   - Don’t cut to a new camera for speech less than 3 secs.
                #   - Cut to a new camera 3 secs BEFORE they start speaking. (L-Cut)
                #   - Cut to a new camera 3 secs AFTER they start speaking. (J-Cut)

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
            logger.exception("Unhandled exception in multipod run: %s", str(e))
            raise
        #################################################

        # After completing the task, update GUI
        progress_bar.stop()
        progress_bar.pack_forget()
        be_patient_label.pack_forget()
        done_label.pack(pady=10)

    def get_speaker_timestamps(self):
        """
        Function to get speaker timestamps by diarizing, reading diarized RTTM file, initializing speaker
        timestamps, and writing timestamps.
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
            logger.exception("Unhandled exception in getting timestamps: %s", str(e))
            raise

    def preprocess_json(self):
        mod_json_2_specs(self.video_1_json, self.video_1_json_mod)
        mod_json_2_specs(self.video_2_json, self.video_2_json_mod)
        self.mts.combine_mod_jsons(
            self.video_1_json_mod,
            self.video_2_json_mod,
            self.filename_1,
            self.filename_2,
        )
