import logging
from importlib import import_module
from importlib.metadata import entry_points
from datetime import datetime
from dynaconf import Dynaconf
import psutil


logger = logging.getLogger(__name__)

FUNCS_MAP = {
    'video-pil': 'screenio.record.record_video_pil',
    'video-ffmpeg': 'screenio.record.record_video_ffmpeg',
    'frames-pil': 'screenio.record.record_frames_pil',
    'frames-ffmpeg': 'screenio.record.record_frames_ffmpeg',
}


def setup_logger(level=0, logger_name=''):
    """setup the root logger"""
    _logger = logging.getLogger(logger_name)
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, level or 0)]
    _logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _logger.addHandler(ch)


def load_settings(path=None):
    settings_files = ['/etc/screenio/settings.toml', 'settings.toml']
    if path:
        settings_files += [path]
    return Dynaconf(settings_files=settings_files)


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
