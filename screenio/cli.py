import sys
from argparse import ArgumentParser, SUPPRESS, REMAINDER
from . import __version__
from . import funcs
from .utils import setup_logger, load_entry_points


def record_cli(argv=None):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='kind')
    parser_video_pil = subparsers.add_parser('video-pil')
    parser_video_pil.add_argument('-o', '--output', default='out.mp4', help='output file')
    parser_video_pil.add_argument('-s', '--size', type=int, nargs=4, help='delta time')
    parser_video_pil.add_argument('-t', '--dt', type=int, default=1, help='delta time')
    parser_video_pil.add_argument('-f', '--framerate', type=int, default=30, help='framerate')
    parser_video_pil.add_argument('-d', '--difference', action='store_false', help='disabel difference check')

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.kind == 'video-pil':
        funcs.record_video_pil(args.output, args.size, args.dt, args.framerate, args.difference)
    elif args.kind == 'frames':
        funcs.record_frames_pil()


def convert_cli(argv):
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
