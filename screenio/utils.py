import logging
from importlib import import_module
from importlib.metadata import entry_points
from datetime import datetime
import psutil


logger = logging.getLogger(__name__)

FUNCS_MAP = {
    'video-pil': 'screenio.record.record_video_pil',
    'video-ffmpeg': 'screenio.record.record_video_ffmpeg',
    'frames-pil': 'screenio.record.record_frames_pil',
    'frames-ffmpeg': 'screenio.record.record_frames_ffmpeg',
}


def create_parsers_pil(parser, name='pil'):
    subparsers = parser.add_parser(name)
    subparsers.add_argument('-s', '--size', type=int, nargs=4, help='size (0, 0, 1920, 1080)')
    subparsers.add_argument('-t', '--dt', type=float, default=1, help='delta time default=1')
    subparsers.add_argument('-f', '--framerate', type=int, default=30, help='framerate default=30')
    subparsers.add_argument('-d', '--difference', action='store_false', help='disabel difference check')
    return subparsers


def create_parsers_ffmpeg(parser, name='ffmpeg', options=['in', 'out']):
    subparsers = parser.add_parser(name)
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


def setup_logger(level=0, logger_name=''):
    """setup the root logger"""
    _logger = logging.getLogger(logger_name)
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, level or 0)]
    _logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _logger.addHandler(ch)


def load_entry_points():
    """get all entry points"""
    return {enp.name: enp.load() for enp in entry_points()['screenio.register_cmd']}


def load_func(name):
    """Import function dynamic"""
    try:
        mod_name, func_name = name.rsplit('.', 1)
        mod = import_module(mod_name)
        return getattr(mod, func_name)
    except Exception as e:
        logger.exception(e, exc_info=True)
    return None


def load_func_map(name, mapper=FUNCS_MAP):
    """Import function dynamic from mapper"""
    return load_func(mapper.get(name))


def format_now(format_str='{}.mp4', format_datetime='%Y-%m-%d_%H-%M-%S'):
    return format_str.format(datetime.now().strftime(format_datetime))


def check_processes(data):
    if not isinstance(data, dict):
        data = {}
    required_processes = list(data.get('required_processes', []))
    prozesse = {p.name() for p in psutil.process_iter() if p.name() in required_processes}
    if len(prozesse) != len(required_processes):
        return False

    banned_processes = list(data.get('banned_processes', []))
    if len([p.name() for p in psutil.process_iter() if p.name() in banned_processes]) > 0:
        return False

    return True
