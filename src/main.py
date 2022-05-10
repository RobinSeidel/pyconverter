import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

from pytube import YouTube

import os
import re

def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        downloads_path = os.path.join(os.path.expanduser('~'), 'downloads')
        if not os.path.exists(downloads_path):
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(downloads_path):
            downloads_path = os.path.expanduser('~')
        return downloads_path

            

class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=2)
        self.rowconfigure(4, weight=2)
        self.rowconfigure(5, weight=3)

        for rowcol in range(3):
            self.columnconfigure(rowcol, weight=1)

        self.quality = tk.StringVar()

        self.setup_widgets()

    def create_heading(self):
        heading = ttk.Label(
            self,
            text="YouTube Downloader",
            justify="center",
            font=("-size", 15, "-weight", "bold"),
        )
        heading.grid(row=0, column=0, columnspan=3)
        return heading

    def create_link_entry_frame(self):
        link_entry_frame = ttk.Frame(self)
        link_entry_frame.grid(row=1, column=0, columnspan=3, sticky="nesw", padx=30)
        link_entry_frame.columnconfigure(0, weight=1)
        link_entry_frame.columnconfigure(1, weight=10)
        return link_entry_frame

    def create_link_entry_label(self, parent):
        link_entry_label = ttk.Label(parent, text="YouTube Link")
        link_entry_label.grid(row=0, column=0, sticky="nesw")
        return link_entry_label

    def create_link_entry(self, parent):
        link_entry = ttk.Entry(parent)
        link_entry.grid(row=0, column=1, columnspan=2, sticky="nesw")
        return link_entry

    def invalidate_widget(self, widget):
        widget.state(["invalid"])

    def validate_widget(self, widget):
        widget.state(["!invalid"])

    def setup_heading(self):
        self.heading = App.create_heading(self)
    
    def validate_youtube_link(self, link):
        return re.match("(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?", link) != None

    def link_event_handler(self, event):
        if self.validate_youtube_link(event.widget.get()):
            self.validate_widget(event.widget)
        else:
            self.invalidate_widget(event.widget)

    def validate_output_path(self, path):
        return os.path.exists(path)

    def output_path_event_handler(self, event):
        if self.validate_output_path(event.widget.get()):
            self.validate_widget(event.widget)
        else:
            self.invalidate_widget(event.widget)


    def bind_entry_validation(self, entry, func):
        entry.bind("<FocusOut>", func)
        entry.bind("<FocusIn>", func)
        entry.bind("<KeyRelease>", func)

    def setup_link_entry(self):
        self.link_entry_frame = self.create_link_entry_frame()
        self.link_entry_label = self.create_link_entry_label(self.link_entry_frame)
        self.link_entry = self.create_link_entry(self.link_entry_frame)
        self.bind_entry_validation(self.link_entry, self.link_event_handler)


    def create_settings_frame(self):
        settings_frame = ttk.LabelFrame(self, text="Quality")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky="nesw", padx=30)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_rowconfigure(0, weight=1)
        return settings_frame

    def create_inner_settings_frame(self, parent):
        inner_settings_frame = ttk.Frame(parent)
        inner_settings_frame.grid(row=0, column=0)
        return inner_settings_frame
    
    def create_settings_radiobuttons(self, parent):
        values = {
            "Low (360p)": "0",
            "Medium (720p)": "1",
            "High (1080p)": "2",
        }

        radiobutton_list = []

        for index, (txt, val) in enumerate(values.items()):
            radiobutton = ttk.Radiobutton(
                parent, text=txt, value=val, variable=self.quality
            )
            radiobutton.pack(expand=True, anchor=tk.W, pady=13)
            radiobutton_list.append(radiobutton)
        return radiobutton_list

    def setup_settings(self):
        self.settings_frame = self.create_settings_frame()
        self.inner_settings_frame = self.create_inner_settings_frame(self.settings_frame)
        self.settings_radiobutton_list = self.create_settings_radiobuttons(
            self.inner_settings_frame
        )

    def choose_output_path(self):
        self.output_entry.delete(0,tk.END)
        path = fd.askdirectory(initialdir=get_download_path())
        self.output_entry.insert(0, path)

    def create_output_entry_frame(self):
        output_entry_frame = ttk.Frame(self)
        output_entry_frame.grid(
            row=4, column=0, columnspan=3, sticky="nesw", padx=30
        )
        output_entry_frame.columnconfigure(0, weight=1)
        output_entry_frame.columnconfigure(1, weight=10)
        return output_entry_frame
    
    def create_output_entry_label(self, parent):
        output_entry_label = ttk.Label(parent, text="Output Path")
        output_entry_label.grid(row=1, column=0, sticky="nesw")
        return output_entry_label

    def create_output_entry(self, parent):
        output_entry = ttk.Entry(parent)
        output_entry.insert(0, get_download_path())
        output_entry.grid(row=1, column=1, sticky="nesw", padx=(0, 3))
        return output_entry

    def create_output_entry_file_button(self, parent):
        output_entry_file_button = ttk.Button(
            self.output_entry_frame, text="Choose", command=self.choose_output_path
        )
        output_entry_file_button.grid(row=1, column=2)
        return output_entry_file_button

    def setup_output_entry(self):
        self.output_entry_frame = self.create_output_entry_frame()
        self.output_entry_label = self.create_output_entry_label(self.output_entry_frame)
        self.output_entry = self.create_output_entry(self.output_entry_frame)
        self.output_entry_file_button = self.create_output_entry_file_button(self.output_entry_frame)
        self.bind_entry_validation(self.output_entry, self.output_path_event_handler) 

    def create_download_button(self, command):
        download_button = ttk.Button(self, text="Download", command=command)
        download_button.grid(row=5, column=0, columnspan=3)
        return download_button
    
    def download_button_callback(self):
        youtube_link = self.link_entry.get()
        output_path = self.output_entry.get()
        if not self.validate_youtube_link(youtube_link):
            return
        if not self.validate_output_path(output_path):
            return
        print(f"All is valid... Downloading {youtube_link} to {output_path}")
        yt = YouTube(youtube_link).streams.first().download(output_path=output_path)


    def setup_download_button(self):
        self.download_button = self.create_download_button(self.download_button_callback)

    def setup_widgets(self):
        self.setup_heading()
        self.setup_link_entry()
        self.setup_settings()
        self.setup_output_entry()
        self.setup_download_button()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simple example")

    root.geometry("600x500")

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
