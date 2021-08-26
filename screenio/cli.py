import sys
from argparse import ArgumentParser, SUPPRESS, REMAINDER
from . import __version__
from . import record
from .octopus import main as octopus_main
from .utils import setup_logger, load_entry_points, format_now


def create_parser_main(commands):
    """Create the main parser"""
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='count', help='verbose level... repeat up to three times.')
    parser.add_argument('command', nargs='?', choices=commands, help='select one command')
    parser.add_argument('argv', help=SUPPRESS, nargs=REMAINDER)
    return parser


def create_parsers_pil(parser):
    subparsers = parser.add_parser('pil')
    subparsers.add_argument('-s', '--size', type=int, nargs=4, help='size (0, 0, 1920, 1080)')
    subparsers.add_argument('-t', '--dt', type=float, default=1, help='delta time default=1')
    subparsers.add_argument('-f', '--framerate', type=int, default=30, help='framerate default=30')
    subparsers.add_argument('-d', '--difference', action='store_false', help='disabel difference check')
    return subparsers


def create_parsers_ffmpeg(parser, options=['in', 'out']):
    subparsers = parser.add_parser('ffmpeg')
    if 'in' in options:
        subparsers.add_argument('-s', '--size', type=int, nargs=2, default=[1920, 1080], help='delta time')
        subparsers.add_argument('-t', '--dt', type=float, default=1, help='delta time default=1')
        subparsers.add_argument('--filename', default=':1', help='ffmpeg input filename for source')
        subparsers.add_argument('--f', default='x11grab', help='vcodec')
    if 'out' in options:
        subparsers.add_argument('-f', '--framerate', type=int, default=30, help='framerate default=30')
        subparsers.add_argument('--vcodec', default='libx264', help='vcodec')
        subparsers.add_argument('--pix_fmt', default='yuv420p', help='pix_fmt')
    return subparsers


def video(argv=None):
    parser = ArgumentParser(prog='screenio video')
    subparsers = parser.add_subparsers(dest='kind')
    subparsers_pil = create_parsers_pil(subparsers)
    subparsers_pil.add_argument('-o', '--output', default=format_now('{}.mp4'), help='output file')
    subparsers_ffmpeg = create_parsers_ffmpeg(subparsers)
    subparsers_ffmpeg.add_argument('-o', '--output', default=format_now('{}.mp4'), help='output file')

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.kind == 'pil':
        record.record_video_pil(args.output, args.size, args.dt, args.framerate, args.difference)
    elif args.kind == 'ffmpeg':
        record.record_video_ffmpeg(args.output, args.filename, args.f, args.size, 1 / args.dt, args.framerate, args.vcodec, args.pix_fmt)
    else:
        parser.print_help()


def frames(argv):
    parser = ArgumentParser(prog='screenio frames')
    subparsers = parser.add_subparsers(dest='kind')
    subparsers_pil = create_parsers_pil(subparsers)
    subparsers_pil.add_argument('-o', '--output', default=format_now('./frames/{}', '%Y-%m-%d'), help='output dir')
    subparsers_ffmpeg = create_parsers_ffmpeg(subparsers, ['in'])
    subparsers_ffmpeg.add_argument('-o', '--output', default=format_now('./frames/{}', '%Y-%m-%d'), help='output dir')

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.kind == 'pil':
        record.record_frames_pil(args.output, args.size, args.dt, args.difference)
    elif args.kind == 'ffmpeg':
        record.record_frames_ffmpeg(args.output, args.size, 1 / args.dt, args.filename, args.f)
    else:
        parser.print_help()


def convert(argv):
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
        record.frames_to_video_moviepy(args.input, args.output, args.framerate)
    elif args.kind == 'ffmpeg':
        record.frames_to_video_ffmpeg(args.input, args.output, args.framerate, args.vcodec, args.pix_fmt)
    else:
        parser.print_help()


def octopus(argv):
    parser = ArgumentParser(prog='screenio dynamic')
    parser.add_argument('-c', '--config', default='screenio.toml', help='config file')
    parser.add_argument('-t', '--dt', type=float, default=60, help='delta time default=60')
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    octopus_main(args.config, args.dt)


def main(argv=None):
    """Create parser und run the dispatch"""
    commands = load_entry_points()
    parser = create_parser_main(commands.keys())
    args = parser.parse_args(argv or sys.argv[1:])

    if args.command:
        setup_logger(args.verbose)
        try:
            return commands[args.command](args.argv)
        except Exception as exc:
            if args.verbose:
                raise
            print('Oh no, a error :(')
            print('Error:', exc)
            print('Run with --verbose for more information.')
            return 0

    return parser.print_help()


if __name__ == '__main__':
    main()
