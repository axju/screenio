import sys
from argparse import ArgumentParser
from time import sleep
from pathlib import Path
from logging import getLogger

import cv2
import numpy as np
import ffmpeg
from PIL.ImageGrab import grab

from .utils import create_parsers_pil, create_parsers_ffmpeg, format_now

logger = getLogger(__name__)


def record_video_pil(output='out.mp4', size=None, dt=1, framerate=30, difference=True, xdisplay=None, running=None):
    current_img = last_img = grab(size, xdisplay=xdisplay)
    output = Path(output).resolve()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output), fourcc, framerate, current_img.size)
    logger.info('start pillow recording with:')
    logger.info('size=%s, framerate=%f, output=%s', size, framerate, output)
    while running is None or not running.is_set():
        try:
            current_img = grab(size, xdisplay=xdisplay)
            if not difference or current_img != last_img:
                logger.debug('add frame running=%s', running)
                frame = np.array(current_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
            else:
                logger.debug('skip frame')
            last_img = current_img
            sleep(dt)
        except KeyboardInterrupt:
            break
    logger.info('end pillow recording')
    out.release()


def record_video_ffmpeg(output='out.mp4', filename=':1', f='x11grab', size=(1920, 1080), framerate=1, fps=30, vcodec='libx264', pix_fmt='yuv420p', running=None):
    """
    framerate -> input framrate for recording the screen
    fps -> output framrate for writing the video file
    """
    output = Path(output).resolve()
    logger.info('start ffmpeg recording with:')
    logger.info('size=%s, framerate=%f, output=%s', size, framerate, output)
    logger.info('fps=%s, vcodec=%s, pix_fmt=%s, filename=%s, f=%s', fps, vcodec, pix_fmt, filename, f)

    stream = ffmpeg.input(filename=filename, f=f, framerate=framerate, video_size=size).setpts('N/TB/{}'.format(fps))
    stream = ffmpeg.output(stream, str(output), vcodec=vcodec, preset='ultrafast', r=fps, pix_fmt=pix_fmt)
    process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
    try:
        if running is None:
            input('')
        else:
            while not running.is_set():
                sleep(1)
    except KeyboardInterrupt:
        logger.info('breack with KeyboardInterrupt')
    finally:
        process.communicate(input=b"q")
        logger.info('end ffmpeg recording')


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
                current_img.save(str(output / '{:06d}.png'.format(counter)))
                counter += 1
            else:
                logger.debug('skip frame')
            last_img = current_img
            sleep(dt)
        except KeyboardInterrupt:
            break
    logger.info('end pillow recording with counter=%i', counter)


def record_frames_ffmpeg(output='frames', size=(1920, 1080), framerate=1, filename=':1', f='x11grab'):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    counter = len(list(output.iterdir()))
    logger.info('start ffmpeg recording with size=%s, framerate=%f, output=%s, counter=%i', size, framerate, output, counter)

    stream = ffmpeg.input(filename=filename, f=f, video_size=size, framerate=framerate)
    stream = ffmpeg.output(stream, str(output / '%06d.png'), start_number=counter, r=1)
    process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
    try:
        input('')
    except KeyboardInterrupt:
        logger.info('breack with KeyboardInterrupt')
    finally:
        process.communicate(input=b"q")
        counter = len(list(output.iterdir())) - 1
        logger.info('end ffmpeg recording with counter=%i', counter)


def main(argv=None):
    parser = ArgumentParser(prog='screenio video')
    subparsers = parser.add_subparsers(dest='kind')
    subparsers_pil = create_parsers_pil(subparsers)
    subparsers_pil.add_argument('-o', '--output', default=format_now('{}.mp4'), help='output file')
    subparsers_ffmpeg = create_parsers_ffmpeg(subparsers)
    subparsers_ffmpeg.add_argument('-o', '--output', default=format_now('{}.mp4'), help='output file')

    subparsers_pil = create_parsers_pil(subparsers, 'pil-frames')
    subparsers_pil.add_argument('-o', '--output', default=format_now('./frames/{}', '%Y-%m-%d'), help='output dir')
    subparsers_ffmpeg = create_parsers_ffmpeg(subparsers, 'ffmpeg-frames', ['in'])
    subparsers_ffmpeg.add_argument('-o', '--output', default=format_now('./frames/{}', '%Y-%m-%d'), help='output dir')


    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.kind == 'pil':
        record_video_pil(args.output, args.size, args.dt, args.framerate, args.difference)
    elif args.kind == 'ffmpeg':
        record_video_ffmpeg(args.output, args.filename, args.f, args.size, 1 / args.dt, args.framerate, args.vcodec, args.pix_fmt)
    elif args.kind == 'pil-frames':
        record_frames_pil(args.output, args.size, args.dt, args.difference)
    elif args.kind == 'ffmpeg-frames':
        record_frames_ffmpeg(args.output, args.size, 1 / args.dt, args.filename, args.f)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
