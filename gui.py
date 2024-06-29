import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class MultiPodGUI:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = tk.Tk()
        self.root.title("MultiPod")
        self.root.geometry("800x400")

        container = tk.Frame(self.root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

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
        print("goodbye")
        if messagebox.askyesno("Quit", "Do you want to quit?"):
            self.root.destroy()


class FRAME_1_file_select(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Initialize the dictionary mapping each file selection area to its label
        self.file_labels = {
            "Shot Angle 1": None,
            "Shot Angle 2": None,
            "Shot Angle 3": None
        }

        # Helper function to create a file selection area
        def create_file_selection_area(angle):
            shot_label = tk.Label(self, text=f"{angle}")
            shot_label.grid(row=int(angle[-1]) - 1, column=0, padx=10, pady=10)
            select_button = ttk.Button(self, text="Select File",
                                       command=lambda: self.select_file(f"{angle}"))
            select_button.grid(row=int(angle[-1]) - 1, column=1, padx=10, pady=20)
            self.file_labels[angle] = tk.Label(self, text="No file selected yet.")
            self.file_labels[angle].grid(row=int(angle[-1]) - 1, column=2, padx=10, pady=10)

        # Create file selection areas using the helper function
        angles = ["1", "2", "3"]
        for angle in angles:
            create_file_selection_area(f"Shot Angle {angle}")

        button1 = ttk.Button(self, text="Next",
                             command=lambda: controller.show_frame(FRAME_2_video_prefs))
        button1.grid(row=3, column=0, columnspan=3, pady=20)

    def select_file(self, angle):
        # Open the file dialog and let the user select a file
        filename = filedialog.askopenfilename(filetypes=[('All Files', '*.*')])
        if filename:
            # Display the selected file name in the label for the specified angle
            self.file_labels[angle].config(text=f"Selected File: {filename}")


class FRAME_2_video_prefs(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button2 = ttk.Button(self, text="Previous",
                             command=lambda: controller.show_frame(FRAME_1_file_select))
        button2.pack(pady=20)

        self.checkbox = tk.Checkbutton(self, text="Select me")
        self.checkbox.pack(pady=20)

        button1 = ttk.Button(self, text="Next",
                             command=lambda: controller.show_frame(FRAME_3_audio_prefs))
        button1.pack(pady=20)


class FRAME_3_audio_prefs(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button1 = ttk.Button(self, text="Previous",
                             command=lambda: controller.show_frame(FRAME_2_video_prefs))
        button1.pack(pady=20)

        self.submit_button = ttk.Button(self, text="Submit Frame 3",
                                        command=lambda: print("Submit button clicked"))
        self.submit_button.pack(pady=20)

        button1 = ttk.Button(self, text="Next",
                             command=lambda: controller.show_frame(FRAME_4_export))
        button1.pack(pady=20)


class FRAME_4_export(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button1 = ttk.Button(self, text="Previous",
                             command=lambda: controller.show_frame(FRAME_3_audio_prefs))
        button1.pack(pady=20)

        self.submit_button = ttk.Button(self, text="Submit Frame 4",
                                        command=lambda: print("Submit button clicked"))
        self.submit_button.pack(pady=20)


if __name__ == "__main__":
    MultiPodGUI()
