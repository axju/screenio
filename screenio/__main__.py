import sys
from argparse import ArgumentParser, SUPPRESS, REMAINDER
from . import __version__
from .utils import setup_logger, load_entry_points


def create_parser(commands):
    """Create the main parser"""
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='count', help='verbose level... repeat up to three times.')
    parser.add_argument('command', nargs='?', choices=commands, help='select one command')
    parser.add_argument('argv', help=SUPPRESS, nargs=REMAINDER)
    return parser


def main(argv=None):
    """Create parser und run the dispatch"""
    commands = load_entry_points()
    parser = create_parser(commands.keys())
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
