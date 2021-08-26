import sys
from argparse import ArgumentParser
from pathlib import Path
from logging import getLogger

import ffmpeg
from moviepy.editor import ImageSequenceClip

from .utils import create_parsers_ffmpeg

logger = getLogger(__name__)


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


def main(argv=None):
    parser = ArgumentParser(prog='screenio convert')
    subparsers = parser.add_subparsers(dest='kind')
    subparsers_moviepy = subparsers.add_parser('moviepy')
    subparsers_moviepy.add_argument('-i', '--input', default='frames', help='input dir')
    subparsers_moviepy.add_argument('-o', '--output', default='out.mp4', help='output file')
    subparsers_moviepy.add_argument('-f', '--framerate', type=int, default=30, help='framerate default=30')

    subparsers_ffmpeg = create_parsers_ffmpeg(subparsers, ['out'])
    subparsers_ffmpeg.add_argument('-i', '--input', default='frames', help='input dir')
    subparsers_ffmpeg.add_argument('-o', '--output', default='out.mp4', help='output file')

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.kind == 'moviepy':
        frames_to_video_moviepy(args.input, args.output, args.framerate)
    elif args.kind == 'ffmpeg':
        frames_to_video_ffmpeg(args.input, args.output, args.framerate, args.vcodec, args.pix_fmt)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
