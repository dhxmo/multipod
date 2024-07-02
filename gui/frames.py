import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from core.MultiPod import MultiPod


class FRAME_1_file_select(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initializes the FRAME_1_file_select object.

        Parameters:
            parent: The parent widget.
            controller: The main controller managing the frames.

        Returns:
            None
        """
        tk.Frame.__init__(self, parent, bg="white")

        welcome_button = ttk.Button(
            self, text="WELCOME", width=40, state="disabled", style="flat.TButton"
        )
        welcome_button.grid(row=0, column=0, columnspan=4, pady=20)

        info_label = tk.Label(
            self,
            text="Sync your videos with the podcast audio and then upload the videos here.",
        )
        info_label.grid(row=1, column=0, columnspan=4, pady=20)

        def select_video_file(label_key, controller, btn):
            """
            A function that opens a file dialog to select a file.
            It updates the label with the selected file name based on the angle provided.

            Parameters:
                label_key: The key to identify the label.
                controller: The controller managing the frames.
                btn: The button to update with the selected file name.

            Returns:
                None
            """
            # Open the file dialog and let the user select a file
            filename = filedialog.askopenfilename(
                filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")]
            )
            if filename:
                # Display the selected file name in the label for the specified angle
                controller.file_labels[label_key].config(text=filename)
                btn.config(text=filename.split("/")[-1])

        def create_file_selection_area(angle):
            """
            Sets labels based on the given angle. Creates a button to select a video file.

            Parameters:
                angle: A string representing the angle. Can be "1", "2", or any other value.

            Returns:
                None
            """
            # set label
            if angle == "1":
                shot_label = tk.Label(self, text=f"Person 1", font=controller.bold_font)
            elif angle == "2":
                shot_label = tk.Label(self, text=f"Person 2", font=controller.bold_font)
            else:
                shot_label = tk.Label(
                    self, text=f"Both People", font=controller.bold_font
                )

            shot_label.grid(row=int(angle[-1]) + 1, column=0, padx=10, pady=10)

            # video select
            video_select_button = ttk.Button(
                self,
                text="Select Video File",
                command=lambda: select_video_file(
                    f"Shot Angle {angle}", controller, video_select_button
                ),
            )
            video_select_button.grid(row=int(angle[-1]) + 1, column=2, padx=10, pady=20)
            controller.file_labels[f"Shot Angle {angle}"] = tk.Label(self, text="")

        # Create file selection areas using the helper function
        angles = ["1", "2", "3"]
        for angle in angles:
            create_file_selection_area(angle)

        button1 = ttk.Button(
            self,
            text="Next",
            width=40,
            command=lambda: controller.show_frame(FRAME_2_video_prefs),
        )
        button1.grid(row=7, column=0, columnspan=4, pady=20)


class FRAME_2_video_prefs(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize the frame with parent and controller.

        Parameters:
            parent: The parent frame.
            controller: The controller for the frame.

        Returns:
            None
        """
        tk.Frame.__init__(self, parent, bg="white")

        prev_button = ttk.Button(
            self,
            text="Previous",
            width=40,
            command=lambda: controller.show_frame(FRAME_1_file_select),
        )
        prev_button.pack(side="top", anchor="center", pady=20)

        self.video_pref_label = tk.Label(
            self, text=f"Video Edit Preferences", font=controller.bold_font
        )
        self.video_pref_label.pack(pady=20)

        self.radio1 = tk.Radiobutton(
            self,
            text="Simple Back and Forth Cuts",
            variable=controller.video_prefs_selection_var,
            value="simple_back_and_forth_cuts",
        )
        self.radio1.pack(anchor="center", pady=20)

        self.radio2 = tk.Radiobutton(
            self,
            text="Creative Cuts",
            variable=controller.video_prefs_selection_var,
            value="creative_cuts",
        )
        self.radio2.pack(anchor="center", pady=20)

        next_button = ttk.Button(
            self,
            text="Next",
            width=40,
            command=lambda: controller.show_frame(FRAME_3_audio_prefs),
        )
        next_button.pack(side="bottom", anchor="center", pady=40)


class FRAME_3_audio_prefs(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initializes the FRAME_3_audio_prefs object.

        Parameters:
            parent: The parent widget.
            controller: The main controller managing the frames.

        Returns:
            None
        """
        tk.Frame.__init__(self, parent, bg="white")

        self.scale_threshold = None
        self.threshold_label = None
        self.controller = controller

        prev_button = ttk.Button(
            self,
            text="Previous",
            width=40,
            command=lambda: controller.show_frame(FRAME_2_video_prefs),
        )
        prev_button.pack(side="top", anchor="center", pady=20)

        audio_prefs_label = tk.Label(
            self, text="Audio Edit Preferences", font=controller.bold_font
        )
        audio_prefs_label.pack(pady=20)

        self.checkbox1 = ttk.Checkbutton(
            self, text="trim silence", variable=controller.trim_silence_var
        )
        self.checkbox1.pack(padx=20, pady=20)

        self.threshold_label = tk.Label(self, text="Threshold")
        self.threshold_label.pack(padx=20, pady=20)
        self.scale_threshold = tk.Scale(
            self,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            resolution=1,
            command=self.update_scale_value,
        )
        self.scale_threshold.pack(padx=20, pady=20)

        self.checkbox2 = ttk.Checkbutton(
            self, text="clean audio", variable=controller.clean_audio_var
        )
        self.checkbox2.pack(padx=20, pady=10)

        next_button = ttk.Button(
            self,
            text="Next",
            width=40,
            command=lambda: controller.show_frame(FRAME_4_export),
        )
        next_button.pack(side="bottom", anchor="center", pady=30)

    def update_scale_value(self, value):
        """Callback function to update self.scale_value with the current scale value."""
        self.controller.threshold_scale_value.set(value)


class FRAME_4_export(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initializes the FRAME_1_file_select object with the parent widget and controller.

        Parameters:
            parent: The parent widget.
            controller: The main controller managing the frames.

        Returns:
            None
        """
        tk.Frame.__init__(self, parent, bg="white")

        prev_button = ttk.Button(
            self,
            text="Previous",
            width=40,
            command=lambda: controller.show_frame(FRAME_3_audio_prefs),
        )
        prev_button.pack(side="top", anchor="center", pady=20)

        self.controller = controller

        self.radio1 = tk.Radiobutton(
            self,
            text="XML (for further editing in your editing suite)",
            variable=controller.export_var,
            value="xml",
        )
        self.radio1.pack(anchor="center", pady=20)

        self.radio2 = tk.Radiobutton(
            self, text="mp4", variable=controller.export_var, value="mp4"
        )
        self.radio2.pack(anchor="center", pady=20)

        self.button1 = ttk.Button(self, text="MultiPod Me!", width=30)
        self.button1.pack(anchor="center", padx=20, pady=20)
        self.button1.bind("<Button-1>", lambda event: self.on_button_click(controller))

        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=200, mode="indeterminate"
        )
        self.be_patient_label = tk.Label(
            self,
            text="Be patient. This takes a while (not as long as doing this manually)",
        )

        self.done_label = tk.Label(
            self, text="DONE! File is stored in ....", font=controller.bold_font
        )

    def on_button_click(self, controller):
        """Method called when the button is clicked, passing the controller object."""
        # if angle 1 or 2 is missing, throw message box
        if (
            controller.file_labels["Shot Angle 1"].cget("text") == ""
            or controller.file_labels["Shot Angle 2"].cget("text") == ""
        ):
            messagebox.showinfo(
                "Input Error",
                "Please select a video file for both "
                "Person 1 and Person 2 shot angles.",
            )
        else:
            file_paths = {}

            for k, v in controller.file_labels.items():
                text = v.cget("text")
                file_paths[k] = text

            if not controller.video_prefs_selection_var.get():
                messagebox.showinfo(
                    "Video Preferences Select",
                    "Please select a valid video preference.",
                )
            else:
                if not controller.export_var.get():
                    messagebox.showinfo(
                        "Output Format Select",
                        "Please select an output format for the export.",
                    )
                elif (
                    controller.export_var.get()
                    and file_paths
                    and controller.video_prefs_selection_var.get()
                ):
                    os.makedirs("assets/sounds/", exist_ok=True)
                    os.makedirs("assets/json/", exist_ok=True)

                    mp = MultiPod(
                        file_paths,
                        controller.video_prefs_selection_var.get(),
                        controller.trim_silence_var.get(),
                        controller.threshold_scale_value.get(),
                        controller.clean_audio_var.get(),
                        controller.export_var.get(),
                    )

                    threading.Thread(
                        target=mp.run,
                        args=(
                            self.progress_bar,
                            self.be_patient_label,
                            self.done_label,
                        ),
                    ).start()
