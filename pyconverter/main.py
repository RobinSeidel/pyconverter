import logging
import tempfile
import traceback
import os
import re
import threading
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox, ttk

from pytube import YouTube

from .exceptions import StreamDoesNotExistError
from .util import get_base_path, get_download_path, combine_video_and_audio


BASE_PATH = get_base_path()

class YouTubeVideo:

    QUALITY_LIST = ["1080p", "720p", "480p", "360p", "240p", "144p"]
    LINK_REGEX = "(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"

    @staticmethod
    def validate_link(link):
        return re.match(YouTubeVideo.LINK_REGEX, link) != None

    @staticmethod
    def validate_path(path):
        return os.path.exists(path) and os.path.isdir(path)

    def __init__(self, link, quality, output_path):
        if not YouTubeVideo.validate_link(link):
            raise ValueError
        if not YouTubeVideo.validate_path(output_path):
            raise ValueError
        if not quality in YouTubeVideo.QUALITY_LIST:
            raise ValueError
        self.quality = quality
        self.output_path = output_path
        self.quality_hierarchy = self.QUALITY_LIST[self.QUALITY_LIST.index(quality) :]
        self.yt = YouTube(link)

    def download_low_quality(self):
        for current_quality in self.quality_hierarchy:
            video_streams = self.yt.streams.filter(
                progressive=True, file_extension="mp4", res=current_quality
            )
            if not video_streams:
                continue
            video_streams.first().download(self.output_path)
            return
        raise StreamDoesNotExistError

    def download_high_quality(self):
        video_streams = self.yt.streams.filter(res="1080p", progressive=False)

        if not video_streams:
            self.quality = "720p"
            self.download_low_quality()
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            video_streams.first().download(tmpdir, filename="video.mp4")
            self.yt.streams.get_audio_only().download(tmpdir, filename="audio.mp4")
            video_path = os.path.join(tmpdir, "video.mp4")
            audio_path = os.path.join(tmpdir, "audio.mp4")
            output_path = os.path.join(
                self.output_path, video_streams.first().default_filename
            )
            combine_video_and_audio(video_path, audio_path, output_path)

    def download(self):
        if self.quality != "1080p":
            self.download_low_quality()
        else:
            self.download_high_quality()


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=2)
        self.rowconfigure(4, weight=2)
        self.rowconfigure(5, weight=2)
        self.rowconfigure(6, weight=2)

        for rowcol in range(3):
            self.columnconfigure(rowcol, weight=1)

        self.quality = tk.StringVar(None, "720p")

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

    def setup_heading(self):
        self.heading = self.create_heading()

    def create_link_entry_frame(self):
        link_entry_frame = ttk.Frame(self)
        link_entry_frame.grid(row=1, column=0, columnspan=3, sticky="nesw", padx=30)
        link_entry_frame.columnconfigure(0, weight=1)
        link_entry_frame.columnconfigure(1, weight=10)
        return link_entry_frame

    def bind_entry_validation(self, entry, func):
        entry.bind("<FocusOut>", func)
        entry.bind("<FocusIn>", func)
        entry.bind("<KeyRelease>", func)

    def create_link_entry_label(self, parent):
        link_entry_label = ttk.Label(parent, text="YouTube Link")
        link_entry_label.grid(row=0, column=0, sticky="nesw")
        return link_entry_label

    def create_link_entry(self, parent):
        link_entry = ttk.Entry(parent)
        link_entry.grid(row=0, column=1, columnspan=2, sticky="nesw")
        return link_entry

    def link_entry_event_handler(self, event):
        if YouTubeVideo.validate_link(event.widget.get()):
            event.widget.state(["!invalid"])
        else:
            event.widget.state(["invalid"])

    def setup_link_entry(self):
        self.link_entry_frame = self.create_link_entry_frame()
        self.link_entry_label = self.create_link_entry_label(self.link_entry_frame)
        self.link_entry = self.create_link_entry(self.link_entry_frame)
        self.bind_entry_validation(self.link_entry, self.link_entry_event_handler)

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
            "Low (360p)": "360p",
            "Medium (720p)": "720p",
            "High (1080p)": "1080p",
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
        self.inner_settings_frame = self.create_inner_settings_frame(
            self.settings_frame
        )
        self.settings_radiobutton_list = self.create_settings_radiobuttons(
            self.inner_settings_frame
        )

    def choose_output_path(self):
        self.output_entry.delete(0, tk.END)
        path = fd.askdirectory(initialdir=get_download_path())
        self.output_entry.insert(0, path)

    def create_output_entry_frame(self):
        output_entry_frame = ttk.Frame(self)
        output_entry_frame.grid(row=4, column=0, columnspan=3, sticky="nesw", padx=30)
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

    def output_entry_event_handler(self, event):
        if YouTubeVideo.validate_path(event.widget.get()):
            event.widget.state(["!invalid"])
        else:
            event.widget.state(["invalid"])

    def setup_output_entry(self):
        self.output_entry_frame = self.create_output_entry_frame()
        self.output_entry_label = self.create_output_entry_label(
            self.output_entry_frame
        )
        self.output_entry = self.create_output_entry(self.output_entry_frame)
        self.output_entry_file_button = self.create_output_entry_file_button(
            self.output_entry_frame
        )
        self.bind_entry_validation(self.output_entry, self.output_entry_event_handler)

    def create_progress_bar(self):
        progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=150, mode="indeterminate"
        )
        progress_bar.grid(row=5, column=0, columnspan=3, sticky="nwse", padx=20)
        return progress_bar

    def setup_progress_bar(self):
        self.progress_bar = self.create_progress_bar()

    def async_download_video(self, youtube_link, quality, output_path):
        self.download_button.grid_remove()
        self.progress_bar.start()

        try:
            YouTubeVideo(youtube_link, quality, output_path).download()
            messagebox.showinfo(
                title="Success", message="The video was downloaded successfully"
            )
        except StreamDoesNotExistError:
            messagebox.showerror(
                "Error", "Could not download the video.\n No stream available"
            )
        except Exception as e:
            message_box_answer = messagebox.askyesno(
                "Error",
                "An Error occured.\n Copy error message to clipboard?",
                icon="error",
            )
            if message_box_answer:
                self.clipboard_clear()
                self.clipboard_append(traceback.format_exc())

        self.progress_bar.stop()
        self.download_button.grid()

    def create_download_button(self, command):
        download_button = ttk.Button(self, text="Download", command=command)
        download_button.grid(row=6, column=0, columnspan=3)
        return download_button

    def download_button_callback(self):
        youtube_link = self.link_entry.get()
        output_path = self.output_entry.get()
        quality = self.quality.get()
        if not YouTubeVideo.validate_link(youtube_link):
            messagebox.showerror("Error", "Please provide a valid YouTube link")
            logging.warning(f"{youtube_link} is not a valid YouTube link")
            return
        if not YouTubeVideo.validate_path(output_path):
            messagebox.showerror("Error", "Please provide a valid output path")
            logging.warning(f"{output_path} is not a valid path")
            return
        logging.info("Starting download thread...")
        threading.Thread(
            target=self.async_download_video, args=(youtube_link, quality, output_path)
        ).start()
        logging.info(f"Downloading {youtube_link} at {quality} to {output_path}...")

    def setup_download_button(self):
        self.download_button = self.create_download_button(
            self.download_button_callback
        )

    def setup_widgets(self):
        self.setup_heading()
        self.setup_link_entry()
        self.setup_settings()
        self.setup_output_entry()
        self.setup_progress_bar()
        self.setup_download_button()

def main():
    root = tk.Tk()
    root.title("YouTube Downloader")
    root.geometry("600x500")
    root.tk.call("source", os.path.join(BASE_PATH, "theme", "sun-valley.tcl"))
    root.tk.call("set_theme", "dark")
    root.iconbitmap(os.path.join(BASE_PATH, "logo", "logo.ico")) 
    app = App(root)
    app.pack(fill="both", expand=True)
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate))
    root.mainloop()
