import tkinter as tk
from tkinter import ttk


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=2)
        self.rowconfigure(4, weight=2)

        for rowcol in range(3):
            self.columnconfigure(rowcol, weight=1)

        self.quality = tk.StringVar()

        self.setup_widgets()

    def setup_widgets(self):

        self.heading = ttk.Label(
            self,
            text="YouTube Downloader",
            justify="center",
            font=("-size", 15, "-weight", "bold"),
        )
        self.heading.grid(row=0, column=0, columnspan=3)

        self.link_entry_frame = ttk.Frame(self)
        self.link_entry_frame.grid(
            row=1, column=0, columnspan=3, sticky="nwes", padx=30
        )

        self.link_entry_frame.columnconfigure(0, weight=1)
        self.link_entry_frame.columnconfigure(1, weight=4)
        self.link_entry_label = ttk.Label(self.link_entry_frame, text="YouTube Link")
        self.link_entry_label.grid(row=0, column=0, sticky="nwes")
        self.link_entry = ttk.Entry(self.link_entry_frame)
        self.link_entry.grid(row=0, column=1, sticky="nwes", padx=(0,75))

        self.settings_frame = ttk.LabelFrame(self, text="Quality")
        self.settings_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=30)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_rowconfigure(0, weight=1)

        self.settings_frame_2 = ttk.Frame(self.settings_frame)
        self.settings_frame_2.grid(row=0, column=0)

        values = {
            "Low (360p)": "0",
            "Medium (720p)": "1",
            "High (1080p)": "2",
        }

        for index, (txt, val) in enumerate(values.items()):
            ttk.Radiobutton(
                self.settings_frame_2, text=txt, value=val, variable=self.quality
            ).pack(expand=True, anchor=tk.W, pady=13)

        self.output_entry_frame = ttk.Frame(self)
        self.output_entry_frame.grid(
            row=2, column=0, columnspan=3, sticky="nwes", padx=30
        )

        self.output_entry_frame.columnconfigure(0, weight=1)
        self.output_entry_frame.columnconfigure(1, weight=4)
        self.output_entry_label = ttk.Label(self.output_entry_frame, text="Output Path")
        self.output_entry_label.grid(row=0, column=0, sticky="nwes")
        self.output_entry = ttk.Entry(self.output_entry_frame)
        self.output_entry.grid(row=0, column=1, sticky="nwes")
        self.output_entry_file_button = ttk.Button(self.output_entry_frame, text="Choose")
        self.output_entry_file_button.grid(row=0, column=2, padx=(5,0))

        self.download_button = ttk.Button(self, text="Download")
        self.download_button.grid(row=4, column=0, columnspan=3)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simple example")

    root.tk.call("source", "theme/sun-valley.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

    root.mainloop()
