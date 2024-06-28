from pytube import YouTube
import ffmpeg
import os
import sys

def video_audio_mux(path_audio_source, path_image_source, out_video_path) -> None:
    video = ffmpeg.input(path_image_source).video
    audio = ffmpeg.input(path_audio_source).audio
    ffmpeg.output(audio, video, out_video_path, vcodec='copy', acodec='copy').run()


def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f'The file "{file_path}" does not exist')


def main() -> None:
    downloads_path = "/downloads/"
    output_path = f".{downloads_path}"

    yt = YouTube(sys.argv[1])

    video_path = (yt.streams.filter(progressive=False, file_extension='mp4')
                  .order_by('resolution').desc().first().download(output_path=output_path))

    audio_stream = (yt.streams.filter(progressive=False, only_audio=True, audio_codec="mp4a.40.2")
                    .order_by('bitrate').desc().first())

    audio_path = audio_stream.download(filename=f"{audio_stream.title.replace("|", "-")}.m4a", output_path=output_path)

    dest_video_path = f"{video_path.split(".")[0]} - muxed.mp4"

    video_audio_mux(audio_path, video_path, dest_video_path)

    delete_file(audio_path)
    delete_file(video_path)

    os.rename(dest_video_path, video_path)


if __name__ == "__main__":
    main()
