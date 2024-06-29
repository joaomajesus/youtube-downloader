from pytube import YouTube
import ffmpeg, os, sys, datetime, re, subprocess


def mux_files(path_audio_source: str, path_image_source: str, path_chapters: str, out_video_path: str) -> None:
    video = ffmpeg.input(path_image_source).video
    audio = ffmpeg.input(path_audio_source).audio
    ffmpeg.output(audio, video, out_video_path, vcodec='copy', acodec='copy').run()

    if path_chapters:
        add_chapters_to_mp4(path_chapters, out_video_path)


def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f'The file "{file_path}" does not exist')


def download_streams(url: str) -> (str, str, str):
    output_path = "downloads/"
    chapters_path = ""
    yt = YouTube(url)

    video_path = (yt
                  .streams
                  .filter(progressive=False,
                          file_extension='mp4')
                  .order_by('resolution')
                  .desc()
                  .first()
                  .download(output_path=output_path))

    audio_stream = (yt
                    .streams
                    .filter(progressive=False,
                            only_audio=True,
                            audio_codec="mp4a.40.2")
                    .order_by('bitrate')
                    .desc()
                    .first())

    path = video_path.split(".")[0]

    audio_path = (audio_stream
                  .download(filename=f"{path}.m4a",
                            output_path=output_path))

    write_description_file(path, yt)

    chapters = get_chapters(yt.description)

    if len(chapters) > 0:
        chapters_path = f"{video_path.split(".")[0]}_chapter.txt"
        write_chapters_file(chapters_path, chapters)

    return audio_path, video_path, chapters_path


def write_description_file(path, yt):
    with open(f"{path}.txt", 'w+b') as fo:
        fo.write(f"From: {yt.watch_url}\n\nDescription:\n\n".encode())
        fo.write(yt.description.encode())


def get_chapters(chapters_str: str) -> list:
    list_of_chapters = []

    line_counter = 1
    for line in chapters_str.split('\n'):
        result = re.search(r"\(?(\d?[:]?\d+[:]\d+)\)?", line)

        try:
            time_count = datetime.datetime.strptime(result.group(1), '%H:%M:%S')
        except:
            try:
                time_count = datetime.datetime.strptime(result.group(1), '%M:%S')
            except:
                continue

        chap_name = line.replace(result.group(0), "").rstrip(' :\n')
        chap_pos = datetime.datetime.strftime(time_count, '%H:%M:%S')
        list_of_chapters.append((str(line_counter).zfill(2), chap_pos, chap_name))
        line_counter += 1

    return list_of_chapters


def write_chapters_file(chapter_file: str, chapter_list: list) -> None:
    """
    Write out the chapter file based on simple MP4 format (OGM)
    """
    with open(chapter_file, 'w+b') as fo:
        for current_chapter in chapter_list:
            fo.write(f'CHAPTER{current_chapter[0]}={current_chapter[1]}\n'.encode())
            fo.write(f'CHAPTER{current_chapter[0]}NAME={current_chapter[2]}\n'.encode())


def add_chapters_to_mp4(chapter_file_name: str, name_for_download: str) -> None:
    """
    Use MP4Box to mux the chapter file with the mp4
    """
    subprocess.run(["MP4Box", "-chap", chapter_file_name, name_for_download])


def main() -> None:
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
