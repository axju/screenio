from time import sleep
from pathlib import Path
from logging import getLogger

import cv2
import ffmpeg
import numpy as np
from PIL.ImageGrab import grab
from moviepy.editor import ImageSequenceClip


logger = getLogger(__name__)


def record_frames_pil(output='frames', size=(0, 0, 1920, 1080), dt=1, difference=True):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    counter = len(list(output.iterdir()))
    logger.info('start pillow recording with size=%s, dt=%f, output=%s, counter=%i', size, dt, output, counter)

    current_img = last_img = grab(size)
    while True:
        try:
            current_img = grab(size)
            if not difference or current_img != last_img:
                logger.debug('save frame')
                current_img.save(str(output / '{:06d}.png'.format(counter)), "JPEG")
                counter += 1
            else:
                logger.debug('skip frame')
            last_img = current_img
            sleep(dt)
        except KeyboardInterrupt:
            break
    logger.info('end pillow recording with counter=%i', counter)


def record_frames_ffmpeg(output='frames', size=(1920, 1080), framerate=1):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    filename = str(output / '%06d.png')
    counter = len(list(output.iterdir()))
    logger.info('start ffmpeg recording with size=%s, framerate=%f, output=%s, counter=%i', size, framerate, output, counter)

    stream = ffmpeg.input(filename=':1', f='x11grab', video_size=size, framerate=framerate)
    stream = ffmpeg.output(stream, filename, start_number=counter, r=1)
    process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
    try:
        input('')
    except KeyboardInterrupt:
        logger.info('breack with KeyboardInterrupt')
    finally:
        process.communicate(input=b"q")
        counter = len(list(output.iterdir())) - 1
        logger.info('end ffmpeg recording with counter=%i', counter)


def record_video_pil(output='out.mkv', size=None, dt=5, framerate=30, difference=True):
    current_img = last_img = grab(size)
    print(current_img.size)
    output = Path(output).resolve()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output), fourcc, 20.0, current_img.size)
    while True:
        try:
            current_img = grab(size)
            if not difference or current_img != last_img:
                logger.debug('add frame')
                frame = np.array(current_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
            else:
                logger.debug('skip frame')
            last_img = current_img
            sleep(dt)
        except KeyboardInterrupt:
            break
    out.release()


def frames_to_video_moviepy(directory='frames', output='out.mp4', fps=30):
    directory = Path(directory).resolve()
    logger.debug('directory=%s', directory)
    files = [str(file) for file in directory.iterdir()]
    files.sort()
    clip = ImageSequenceClip(files, fps=fps)
    clip.write_videofile(str(output))


def frames_to_video_ffmpeg(directory='frames', output='out.mp4', fps=30, vcodec='libx264', pix_fmt='yuv420p'):
    directory = Path(directory).resolve()
    filename = str(directory / '%06d.png')
    stream = ffmpeg.input(filename=filename, f='image2').setpts('N/TB/{}'.format(fps))
    stream = ffmpeg.output(stream, output, vcodec=vcodec, pix_fmt=pix_fmt, r=fps)
    ffmpeg.run(stream, overwrite_output=True)
