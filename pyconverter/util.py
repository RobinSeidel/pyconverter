# Some static utility methods
import os
import sys
import logging
import ffmpeg


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_download_path_win():
    import winreg

    sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            download_path = winreg.QueryValueEx(key, downloads_guid)[0]
    except (FileNotFoundError, WindowsError):
        logging.warning("Could not determine windows downloads path")
        download_path = ""
    logging.info(f"Detected downloads path is {download_path}")
    return download_path


def get_download_path_unix():
    downloads_path = os.path.join(os.path.expanduser("~"), "downloads")
    if not os.path.exists(downloads_path):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.exists(downloads_path):
        downloads_path = os.path.expanduser("~")
        logging.warning("Could not determine linux downloads path")
    logging.info(f"Detected downloads path is {downloads_path}")
    return downloads_path


def get_download_path():
    if os.name == "nt":
        return get_download_path_win()
    else:
        return get_download_path_unix()


def combine_video_and_audio(video_path, audio_path, output_path):
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)
    ffmpeg.concat(video, audio, v=1, a=1).output(output_path).run(overwrite_output=True)
