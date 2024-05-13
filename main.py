import yt_dlp
import cv2
import numpy as np
import time
import os
import ctypes

# ANSI escape codes for colors, now including 256-color support
def rgb_to_ansi(r, g, b):
    if r == g == b:
        if r < 8:
            return '\033[38;5;16m'  # Black
        if r > 248:
            return '\033[38;5;231m'  # White
        return f'\033[38;5;{232 + (r-8)//11}m'  # Grayscale from 232 to 255
    return f'\033[38;5;{16 + (36 * (r//43) + 6 * (g//43) + (b//43))}m'

def frame_to_ascii(frame, cols=240, scale=0.43):
    height, width, _ = frame.shape
    cell_width = width / cols
    cell_height = cell_width / scale
    rows = int(height / cell_height)

    resized_color_frame = cv2.resize(frame, (cols, rows))

    ascii_chars = "@%#*+=-:. "
    ascii_frame = ""

    for i in range(rows):
        for j in range(cols):
            pixel = resized_color_frame[i, j]
            color = rgb_to_ansi(pixel[2], pixel[1], pixel[0])
            gray = 0.2989 * pixel[2] + 0.5870 * pixel[1] + 0.1140 * pixel[0]
            char = ascii_chars[int(gray / 255 * (len(ascii_chars) - 1))]
            ascii_frame += color + char
        ascii_frame += '\033[0m' + '\n'

    return ascii_frame

#Set the console window size based on calculated dimensions.
def set_console_window_aspect(cols, rows):
    os.system(f'mode con: cols={cols} lines={rows}')

#Stream a YouTube video in ASCII with color and frame rate control.
def stream_youtube_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]/bestaudio[ext=m4a]/best',
        'noplaylist': True,
        'verbose': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict.get('url', None)
        fps = info_dict.get('fps', 30)
        width = info_dict.get('width')
        height = info_dict.get('height')

    if video_url is None:
        print("Failed to retrieve video URL.")
        return
    
    cap = cv2.VideoCapture(video_url)
    frame_time = 1.0 / fps

    # Resize the console window
    set_console_window_aspect(240, int(height / width * 240 * 0.5))  # Adjusted for typical character height/width ratio

    try:
        next_frame_time = time.time() + frame_time
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to retrieve frame.")
                break
            
            current_time = time.time()
            if current_time < next_frame_time:
                ascii_art = frame_to_ascii(frame)
                print(ascii_art)
                time_to_sleep = next_frame_time - current_time
                time.sleep(time_to_sleep)
                next_frame_time += frame_time
            else:
                # Skip processing this frame to catch up
                next_frame_time += frame_time
    finally:
        cap.release()

youtube_url = input("Enter YouTube URL: ")
stream_youtube_video(youtube_url)