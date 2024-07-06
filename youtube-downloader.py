from pytube import YouTube
import ffmpeg
import os
import sys
import datetime
import re
import subprocess


def mux_files(
    audio_source_spath: str,
    image_source_path: str,
    chapters_path: str,
    out_video_path: str,
) -> None:
    """
    Muxes audio and video files into a single output video.

    Args:
        audio_source_spath (str): The path to the audio file.
        image_source_path (str): The path to the video file.
        chapters_path (str): The path to the chapters file (optional).
        out_video_path (str): The path to the output video file.

    Returns:
        None
    """
    video = ffmpeg.input(image_source_path).video
    audio = ffmpeg.input(audio_source_spath).audio
    ffmpeg.output(audio, video, out_video_path, vcodec="copy", acodec="copy").run()

    if chapters_path:
        add_chapters_to_mp4(chapters_path, out_video_path)


def delete_file(file_path: str) -> None:
    """
    Deletes a file at the given file path.

    Args:
        file_path (str): The path to the file to be deleted.

    Returns:
        None: This function does not return anything.

    Raises:
        FileNotFoundError: If the file specified by `file_path` does not exist.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f'The file "{file_path}" does not exist')


def download_streams(url: str) -> (str, str, str):
    """
    Downloads audio and video streams from a given URL, extracts audio and video paths, writes a description file,
    and retrieves chapters if available.

    Args:
        url (str): The URL of the video to download.

    Returns:
        tuple: A tuple containing the path to the audio file, path to the video file,
        and path to the chapters file (if available).
    """
    output_path = "downloads/"
    chapters_path = ""
    yt = YouTube(url)

    video_path = (
        yt.streams.filter(progressive=False, file_extension="mp4")
        .order_by("resolution")
        .desc()
        .first()
        .download(output_path=output_path)
    )

    audio_stream = (
        yt.streams.filter(progressive=False, only_audio=True, audio_codec="mp4a.40.2")
        .order_by("bitrate")
        .desc()
        .first()
    )

    path = video_path.split(".")[0]

    audio_path = audio_stream.download(filename=f"{path}.m4a", output_path=output_path)

    write_description_file(path, yt)

    chapters = get_chapters(yt.description)

    if len(chapters) > 0:
        chapters_path = f"{video_path.split(".")[0]}_chapter.txt"
        write_chapters_file(chapters_path, chapters)

    return audio_path, video_path, chapters_path


def write_description_file(path: str, yt: YouTube):
    """
    Write the description of a YouTube video to a file.

    Parameters:
        path (str): The path to the file where the description will be written.
        yt (YouTube): The YouTube object containing the video information.

    Returns:
        None
    """
    with open(f"{path}.txt", "w+b") as fo:
        fo.write(f"From: {yt.watch_url}\n\nDescription:\n\n".encode())
        fo.write(yt.description.encode())


def get_chapters(description: str) -> list:
    """
    Parses a string of chapters to extract the chapter positions and names.

    Parameters:
        description (str): A string containing chapter information.

    Returns:
        list: A list of tuples containing chapter number, position, and name.
    """
    list_of_chapters = []

    line_counter = 1
    for line in description.split("\n"):
        result = re.search(r"\(?(\d?:?\d+:\d+)\)?", line)

        try:
            time_count = datetime.datetime.strptime(result.group(1), "%H:%M:%S")
        except:
            try:
                time_count = datetime.datetime.strptime(result.group(1), "%M:%S")
            except:
                continue

        chap_name = line.replace(result.group(0), "").rstrip(" :\n")
        chap_pos = datetime.datetime.strftime(time_count, "%H:%M:%S")
        list_of_chapters.append((str(line_counter).zfill(2), chap_pos, chap_name))
        line_counter += 1

    return list_of_chapters


def write_chapters_file(chapter_file_path: str, chapters: list) -> None:
    """
    Write out the chapter file based on simple MP4 format (OGM).

    Args:
        chapter_file_path (str): The path to the chapter file.
        chapters (list): A list of tuples containing chapter information.
            Each tuple should have the following structure: (chapter_number, chapter_position, chapter_name).

    Returns:
        None
    """
    with open(chapter_file_path, "w+b") as fo:
        for current_chapter in chapters:
            fo.write(f"CHAPTER{current_chapter[0]}={current_chapter[1]}\n".encode())
            fo.write(f"CHAPTER{current_chapter[0]}NAME={current_chapter[2]}\n".encode())


def add_chapters_to_mp4(chapter_file_path: str, mp4_file_path: str) -> None:
    """
    Add chapters to an MP4 file using MP4Box.

    Args:
        chapter_file_path (str): The path to the chapter file.
        mp4_file_path (str): The name for the downloaded MP4 file.

    Returns:
        None
    """
    subprocess.run(["MP4Box", "-chap", chapter_file_path, mp4_file_path])


def main() -> None:
    """
    Downloads audio and video streams from a given URL, muxes them into a single video file,
    and performs additional operations such as deleting temporary files and renaming the output file.

    Returns:
        None
    """
    audio_path, video_path, chapters_path = download_streams(sys.argv[1])

    dest_video_path: str = f"{video_path.split(".")[0]} - muxed.mp4"

    mux_files(audio_path, video_path, chapters_path, dest_video_path)

    delete_file(audio_path)
    delete_file(video_path)

    if chapters_path:
        delete_file(chapters_path)

    os.rename(dest_video_path, video_path)


if __name__ == "__main__":
    main()
