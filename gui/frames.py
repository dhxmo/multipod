import re
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from multipod.MultiPod import MultiPod


def select_file(angle, controller):
    # Open the file dialog and let the user select a file
    filename = filedialog.askopenfilename(filetypes=[('Video Files', '*.mp4 *.avi *.mkv *.mov')])
    if filename:
        # Display the selected file name in the label for the specified angle
        controller.file_labels[angle].config(text=f"Selected File: {filename}")


class FRAME_1_file_select(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='white')

        prev_button = ttk.Button(self, text="WELCOME", width=40, state="disabled", style='flat.TButton')
        prev_button.pack(side="top", anchor="center", pady=20)

        # Helper function to create a file selection area
        def create_file_selection_area(angle):
            if angle == "Shot Angle 1":
                shot_label = tk.Label(self, text=f"Person 1 Angle", font=controller.bold_font)
            elif angle == "Shot Angle 2":
                shot_label = tk.Label(self, text=f"Person 2 Angle", font=controller.bold_font)
            else:
                shot_label = tk.Label(self, text=f"Both Angle", font=controller.bold_font)

            # Add the file selection area to the grid
            shot_label.pack(anchor="center", padx=10, pady=10)
            select_button = ttk.Button(self, text="Select File",
                                       command=lambda: select_file(f"{angle}", controller))
            select_button.pack(anchor="center", padx=10, pady=20)
            controller.file_labels[angle] = tk.Label(self, text="No file selected yet.")
            controller.file_labels[angle].pack(anchor="center", padx=10, pady=10)

        # Create file selection areas using the helper function
        angles = ["1", "2", "3"]
        for angle in angles:
            create_file_selection_area(f"Shot Angle {angle}")

        button1 = ttk.Button(self, text="Next", width=40,
                             command=lambda: controller.show_frame(FRAME_2_video_prefs))
        button1.pack(side="bottom", anchor="center", pady=40)


class FRAME_2_video_prefs(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='white')

        prev_button = ttk.Button(self, text="Previous", width=40,
                                 command=lambda: controller.show_frame(FRAME_1_file_select))
        prev_button.pack(side="top", anchor="center", pady=20)

        self.video_pref_label = tk.Label(self, text=f"Video Edit Preferences", font=controller.bold_font)
        self.video_pref_label.pack(pady=20)

        # Radio button for simple back and forth cuts
        self.radio1 = tk.Radiobutton(self, text="Simple Back and Forth Cuts",
                                     variable=controller.video_prefs_selection_var,
                                     value="simple_back_and_forth_cuts")
        self.radio1.pack(anchor='center', pady=20)

        # Radio button for creative cuts
        self.radio2 = tk.Radiobutton(self, text="Creative Cuts", variable=controller.video_prefs_selection_var,
                                     value="creative_cuts")
        self.radio2.pack(anchor='center', pady=20)

        next_button = ttk.Button(self, text="Next", width=40,
                                 command=lambda: controller.show_frame(FRAME_3_audio_prefs))
        next_button.pack(side="bottom", anchor="center", pady=40)


class FRAME_3_audio_prefs(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='white')

        self.scale_threshold = None
        self.threshold_label = None

        prev_button = ttk.Button(self, text="Previous", width=40,
                                 command=lambda: controller.show_frame(FRAME_2_video_prefs))
        prev_button.pack(side="top", anchor="center", pady=20)

        audio_prefs_label = tk.Label(self, text="Audio Edit Preferences", font=controller.bold_font)
        audio_prefs_label.pack(pady=20)

        self.checkbox1 = ttk.Checkbutton(self, text="trim silence", variable=controller.trim_silence_var)
        self.checkbox1.pack(padx=20, pady=20)

        # Label for the Threshold scale
        self.controller = controller

        self.threshold_label = tk.Label(self, text="Threshold")
        self.threshold_label.pack(padx=20, pady=20)
        self.scale_threshold = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL,
                                        resolution=1, command=self.update_scale_value)
        self.scale_threshold.pack(padx=20, pady=20)

        self.checkbox2 = ttk.Checkbutton(self, text="clean audio", variable=controller.clean_audio_var)
        self.checkbox2.pack(padx=20, pady=20)

        next_button = ttk.Button(self, text="Next", width=40,
                                 command=lambda: controller.show_frame(FRAME_4_export))
        next_button.pack(side="bottom", anchor="center", pady=40)
        # button1.grid(row=5, column=2, padx=20, pady=20)

    def update_scale_value(self, value):
        """Callback function to update self.scale_value with the current scale value."""
        self.controller.threshold_scale_value.set(value)


class FRAME_4_export(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='white')

        prev_button = ttk.Button(self, text="Previous", width=40,
                                 command=lambda: controller.show_frame(FRAME_3_audio_prefs))
        prev_button.pack(side="top", anchor="center", pady=20)

        self.controller = controller

        self.radio1 = tk.Radiobutton(self, text="XML (for further editing in your editing suite)",
                                     variable=controller.export_var,
                                     value="xml")
        self.radio1.pack(anchor='center', pady=20)

        self.radio2 = tk.Radiobutton(self, text="mp4",
                                     variable=controller.export_var,
                                     value="mp4")
        self.radio2.pack(anchor='center', pady=20)

        self.button1 = ttk.Button(self, text="MultiPod Me!", width=30)
        self.button1.pack(anchor="center", padx=20, pady=20)
        self.button1.bind('<Button-1>', lambda event: self.on_button_click(controller))

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, mode="indeterminate")

    def on_button_click(self, controller):
        """Method called when the button is clicked, passing the controller object."""
        # if angle 1 or 2 is missing, throw message box
        if not controller.file_labels["Shot Angle 1"].cget("text") or not controller.file_labels["Shot Angle 2"].cget(
                "text"):
            messagebox.showinfo("Input Video Select", "Please select a video for Person 1 and Person 2 shot angles.")
        else:
            file_paths = {}

            for k, v in controller.file_labels.items():
                text = v.cget("text")
                pattern = r"(?<=Selected File: ).*"
                match = re.search(pattern, text)

                if k == "Shot Angle 1" and not match:
                    messagebox.showinfo("Input Video Select", "Please select a video for Person 1 shot angle.")
                elif k == "Shot Angle 2" and not match:
                    messagebox.showinfo("Input Video Select", "Please select a video for Person 2 shot angle.")
                elif match:
                    file_path = match.group(0)
                    file_paths[k] = file_path

            if not controller.video_prefs_selection_var.get():
                messagebox.showinfo("Video Preferences Select", "Please select a valid video preference.")
            else:
                if not controller.export_var.get():
                    messagebox.showinfo("Output Format Select", "Please select an output format for the export.")
                elif controller.export_var.get() and file_paths and controller.video_prefs_selection_var.get():
                    mp = MultiPod(file_paths,
                                  controller.video_prefs_selection_var.get(),
                                  controller.trim_silence_var.get(),
                                  controller.threshold_scale_value.get(),
                                  controller.clean_audio_var.get(),
                                  controller.export_var.get())

                    threading.Thread(target=mp.run, args=(self.progress_bar,)).start()
