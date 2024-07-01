import tkinter as tk
from tkinter import ttk, messagebox, font

import ttkthemes

from gui.frames import FRAME_1_file_select, FRAME_2_video_prefs, FRAME_3_audio_prefs, FRAME_4_export


class MultiPodGUI:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = tk.Tk()
        self.root.title("MultiPod")

        self.root.geometry("500x600")
        self.root.configure(background='white')
        self.root.resizable(False, False)
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=10)
        self.root.option_add("*Font", default_font)

        s = ttk.Style(self.root)
        s.configure('flat.TButton', borderwidth=0)

        style = ttkthemes.ThemedStyle()
        style.set_theme("breeze")

        # Define a bold font
        self.bold_font = font.Font(family="Arial", size=15, weight="bold")

        container = tk.Frame(self.root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Step 1
        self.file_labels = {
            "Shot Angle 1": None,
            "Shot Angle 2": None,
            "Shot Angle 3": None,
            # "Audio File": None,
        }

        # Step 2
        self.video_prefs_selection_var = tk.StringVar()

        # Step 3
        self.trim_silence_var = tk.BooleanVar()
        self.threshold_scale_value = tk.DoubleVar()
        self.clean_audio_var = tk.BooleanVar()

        # Step 4
        self.export_var = tk.StringVar()

        self.frames = {}
        for F in (FRAME_1_file_select, FRAME_2_video_prefs, FRAME_3_audio_prefs, FRAME_4_export):
            frame = F(container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F] = frame

        self.current_frame = FRAME_1_file_select

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.show_frame(self.current_frame)

        self.root.mainloop()

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def close(self):
        if messagebox.askyesno("Quit", "Do you want to quit?"):
            self.root.destroy()
