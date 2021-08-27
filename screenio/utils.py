import logging
from importlib import import_module
from importlib.metadata import entry_points
from pathlib import Path
from datetime import datetime
from time import sleep
from threading import Thread, Event

import psutil
from watchdog.events import PatternMatchingEventHandler


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


def check_processes(required=[], required_files=[], banned=[], banned_files=[]):
    if not required and not required_files and not required_files and not banned_files:
        return True

    processes, processes_files = [], []
    for proc in psutil.process_iter():
        if proc.name() in required:
            processes.append(proc.name())
        if proc.name() in banned:
            return False
        try:
            for item in proc.open_files():
                for name in required_files:
                    if item.path.startswith(name):
                        processes_files.append(name)
                for name in banned_files:
                    if item.path.startswith(name):
                        return False
        except Exception:
            pass
    return len(set(processes)) == len(required) and len(set(processes_files)) == len(required_files)


def check_triggers(current, target):
    if target:
        return all([tag in current for tag in target])
    return len(current) > 0


def check_open_file(fpath):
    path = str(fpath)
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if path == item.path:
                    return True
        except Exception:
            pass
    return False


class FileSystemHandler(PatternMatchingEventHandler):

    def __init__(self, name, on_action, patterns=['*.py']):
        super().__init__(patterns=patterns, ignore_directories=True, case_sensitive=False)
        self.name, self.on_action = name, on_action

    def on_any_event(self, event):
        self.on_action(self.name, event)


class BasicTrigger(Thread):
    """docstring for MouseKeyboardTrigger."""

    def __init__(self, config, on_trigger, dt=5):
        super().__init__()
        self.logger = logging.getLogger('.'.join([__name__, self.__class__.__name__]))
        self.config, self.on_trigger, self.dt = config, on_trigger, dt
        self._actions, self.running = [], Event()
        self.start()

    def wait(self):
        for _ in range(self.dt):
            sleep(1)

    def close(self):
        self.logger.debug('stop thread')
        self.running.set()

    def action(self, name, event):
        if event and name not in self._actions:
            self.on_trigger(self.__class__.__name__, name, True)
            self._actions.append(name)
        elif not event and name in self._actions:
            self.on_trigger(self.__class__.__name__, name, False)
            self._actions.remove(name)


class FuncRunner(Thread):

    def __init__(self, func='screenio.record.record_video_pil', directory='.', filename='{}.mp4', kwargs={}):
        super().__init__()
        self.running = Event()
        if isinstance(func, str):
            self.func = load_func(func)
        else:
            self.func = func

        directory = Path(directory).resolve()
        directory.mkdir(parents=True, exist_ok=True)

        self.kwargs = kwargs
        self.kwargs['output'] = str(Path(directory).resolve() / format_now(filename))
        self.start()

    def stop(self):
        logger.debug('stop thread')
        self.running.set()

    def run(self):
        logger.debug('run thread')
        self.func(**self.kwargs, running=self.running)
