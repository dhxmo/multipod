import tkinter as tk
from tkinter import ttk, messagebox


class MyGUI:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = tk.Tk()
        self.root.title("multipod")
        self.root.geometry("800x400")

        container = tk.Frame(self.root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, Page1, Page2):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.show_frame(StartPage)

        self.root.mainloop()

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def close(self):
        print("goodbye")
        if messagebox.askyesno("Quit", "Do you want to quit?"):
            self.root.destroy()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.text_box = tk.Text(self, height=5, width=30)
        self.text_box.pack(pady=20)

        button1 = ttk.Button(self, text="Next",
                             command=lambda: controller.show_frame(Page1))
        button1.pack(pady=20)


class Page1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button2 = ttk.Button(self, text="Previous",
                             command=lambda: controller.show_frame(StartPage))
        button2.pack(pady=20)

        self.checkbox = tk.Checkbutton(self, text="Select me")
        self.checkbox.pack(pady=20)

        button1 = ttk.Button(self, text="Next",
                             command=lambda: controller.show_frame(Page2))
        button1.pack(pady=20)


class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button1 = ttk.Button(self, text="Previous",
                             command=lambda: controller.show_frame(Page1))
        button1.pack(pady=20)

        self.submit_button = ttk.Button(self, text="Submit",
                                        command=lambda: print("Submit button clicked"))
        self.submit_button.pack(pady=20)


if __name__ == "__main__":
    MyGUI()
