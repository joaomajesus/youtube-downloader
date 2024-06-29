# YouTube Downloader
A simple Python script to download YouTube videos.
## Features:
- Downloads the highest resolution video stream and highest bitrate audio stream and muxes them together.
- Extracts the video chapters from the description and adds them to the video.
- Saves the video url and description into a text file.
## Requirements
- Install [ffmpeg](https://www.ffmpeg.org/download.html)
- Install [GPAC](https://gpac.io/downloads/gpac-nightly-builds/)
- Create a virtual environment: ```python -m venv .venv```   
- Activate environment:
  - Windows: ```.venv/Scripts/activate```
  - Linux/MacOS: ```source .venv/bin/activate```
- Install requirements: ```pip install -r requirements.txt```
## Usage
```shell
python main.py "<YouTubeVideoUrl>"
```
example:
```shell
python main.py "https://www.youtube.com/watch?v=cJbvcH0JNGA"
```