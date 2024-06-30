from pathlib import Path


class MultiPod:
    def __init__(self, file_paths, video_prefs_selection_var, trim_silence_var,
                 threshold_scale_value, clean_audio_var, export_var):
        self.camera_1_video_path = None
        self.camera_2_video_path = None
        self.camera_3_video_path = None
        self.audio_path = None

        for k, v in file_paths.items():
            if v != "No file selected yet.":
                if k == "Shot Angle 1":
                    self.camera_1_video_path = Path(v)
                elif k == "Shot Angle 2":
                    self.camera_2_video_path = Path(v)
                elif k == "Shot Angle 3":
                    self.camera_3_video_path = Path(v)
                elif k == "Audio File 1":
                    self.audio_path = Path(v)

        self.video_prefs_selection_var = video_prefs_selection_var
        self.trim_silence_var = trim_silence_var
        self.threshold_scale_value = threshold_scale_value
        self.clean_audio_var = clean_audio_var
        self.export_var = export_var

    def run(self, progress_bar, done_label):
        # Start the progress bar animation
        progress_bar.pack(pady=10)
        progress_bar.start()

        print("self.camera_1_video_path", self.camera_1_video_path)
        print("self.camera_2_video_path", self.camera_2_video_path)
        print("self.camera_3_video_path", self.camera_3_video_path)
        print("self.audio_path_1", self.audio_path)
        print("video_prefs_selection_var: ", self.video_prefs_selection_var)
        print("trim_silence_var: ", self.trim_silence_var)
        print("threshold_scale_value: ", self.threshold_scale_value)
        print("clean_audio_var: ", self.clean_audio_var)
        print("export_var: ", self.export_var)

        #################################################
        # all the multipod processing happens here
        # Control Flow:

        # STEP 2: sync videos with voice diarization

        # STEP 3: if video_prev -> simple cuts -> cut video together simply
        # else -> creative cuts -> cut together with J/L
        #   - If Shot Angle 3 is not none ->  footage available, Cut to a wide angle if more than one person is talking.
        #   - Don’t cut away if someone is monologuing more than 30 secs. Even if they’re briefly interrupted.
        #   - Don’t cut to a new camera for speech less than 3 secs.
        #   - Cut to a new camera 3 secs BEFORE they start speaking. (L-Cut)
        #   - Cut to a new camera 3 secs AFTER they start speaking. (J-Cut)
        #   - Don’t cut to Person D if they talk.
        #
        # STEP 4: if audio_prev -> trim silence -> trim
        #
        # STEP 5: if audio_prev -> clean audio ->
        # - remove unnecessary words uhh like etc.
        # - make audio very clean and professional.
        # - remove echoes, breath sounds, click pops, etc.
        #
        # STEP 6: if export_prev -> mp4/xml -> export in the correct format

        #################################################

        # After completing the task, update GUI
        progress_bar.stop()  # Stop the progress bar
        progress_bar.pack_forget()
        done_label.pack(pady=10)
