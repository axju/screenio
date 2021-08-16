import sys
from argparse import ArgumentParser, SUPPRESS, REMAINDER
from . import __version__
from . import funcs
from .utils import setup_logger, load_entry_points


def video(argv=None):
    parser = ArgumentParser(prog='screenio video')
    subparsers = parser.add_subparsers(dest='kind')
    subparsers_pil = subparsers.add_parser('pil')
    subparsers_pil.add_argument('-o', '--output', default='out.mp4', help='output file')
    subparsers_pil.add_argument('-s', '--size', type=int, nargs=4, help='size 0 0 1920 1080)')
    subparsers_pil.add_argument('-t', '--dt', type=float, default=1, help='delta time default=1')
    subparsers_pil.add_argument('-f', '--framerate', type=int, default=30, help='framerate default=30')
    subparsers_pil.add_argument('-d', '--difference', action='store_false', help='disabel difference check')

    subparsers_ffmpeg = subparsers.add_parser('ffmpeg')
    subparsers_ffmpeg.add_argument('-o', '--output', default='out.mp4', help='output file')
    subparsers_ffmpeg.add_argument('-s', '--size', type=int, nargs=2, default=[1920, 1080], help='delta time')
    subparsers_ffmpeg.add_argument('-t', '--dt', type=float, default=1, help='delta time default=1')
    subparsers_ffmpeg.add_argument('-f', '--framerate', type=int, default=30, help='framerate default=30')
    subparsers_ffmpeg.add_argument('--filename', default=':1', help='ffmpeg input filename for source')
    subparsers_ffmpeg.add_argument('--f', default='x11grab', help='vcodec')
    subparsers_ffmpeg.add_argument('--vcodec', default='libx264', help='vcodec')
    subparsers_ffmpeg.add_argument('--pix_fmt', default='yuv420p', help='pix_fmt')

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.kind == 'pil':
        funcs.record_video_pil(args.output, args.size, args.dt, args.framerate, args.difference)
    elif args.kind == 'ffmpeg':
        funcs.record_video_ffmpeg(args.output, args.filename, args.f, args.size, 1 / args.dt, args.framerate, args.vcodec, args.pix_fmt)
    else:
        parser.print_help()


def frames(argv):
    parser = ArgumentParser(prog='screenio frames')
    subparsers = parser.add_subparsers(dest='kind')
    subparsers_pil = subparsers.add_parser('pil')
    subparsers_pil.add_argument('-o', '--output', default='frames', help='output dir')
    subparsers_pil.add_argument('-s', '--size', type=int, nargs=4, help='size (0, 0, 1920, 1080)')
    subparsers_pil.add_argument('-t', '--dt', type=int, default=1, help='delta time default=1')
    subparsers_pil.add_argument('-d', '--difference', action='store_false', help='disabel difference check')

    subparsers_ffmpeg = subparsers.add_parser('ffmpeg')
    subparsers_ffmpeg.add_argument('-o', '--output', default='frames', help='output dir')
    subparsers_ffmpeg.add_argument('-s', '--size', type=int, nargs=2, default=[1920, 1080], help='size default=(1920, 1080)')
    subparsers_ffmpeg.add_argument('-f', '--framerate', type=int, default=1, help='framerate default=1')

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.kind == 'pil':
        funcs.record_frames_pil(args.output, args.size, args.dt, args.difference)
    elif args.kind == 'ffmpeg':
        funcs.record_frames_ffmpeg(args.output, args.size, args.framerate)
    else:
        parser.print_help()

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])


def convert(argv):
    funcs.frames_to_video_ffmpeg()


def create_main_parse(commands):
    """Create the main parser"""
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('-s', '--settings', help='Set an alternative settings file.')
    parser.add_argument('-v', '--verbose', action='count', help='verbose level... repeat up to three times.')
    parser.add_argument('command', nargs='?', choices=commands, help='select one command')
    parser.add_argument('argv', help=SUPPRESS, nargs=REMAINDER)
    return parser


def main(argv=None):
    """Create parser und run the dispatch"""
    commands = load_entry_points()
    parser = create_main_parse(commands.keys())
    args = parser.parse_args(argv or sys.argv[1:])

    if args.command:
        setup_logger(args.verbose)
        # settings = load_settings(args.settings)
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
