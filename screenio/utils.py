import logging
from importlib import import_module
from importlib.metadata import entry_points
from datetime import datetime
from dynaconf import Dynaconf


logger = logging.getLogger(__name__)

FUNCS_MAP = {
    'video-pil': 'screenio.funcs.record_video_pil',
    'video-ffmpeg': 'screenio.funcs.record_video_ffmpeg',
    'frames-pil': 'screenio.funcs.record_frames_pil',
    'frames-ffmpeg': 'screenio.funcs.record_frames_ffmpeg',
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


def load_func(name, mapper=FUNCS_MAP):
    """Import function dynamic"""
    try:
        mod_name, func_name = mapper.get(name).rsplit('.', 1)
        mod = import_module(mod_name)
        return getattr(mod, func_name)
    except Exception as e:
        logger.exception(e, exc_info=True)
    return None


def format_now(format_str='{}.mp4', format_datetime='%Y-%m-%d_%H-%M-%S'):
    return format_str.format(datetime.now().strftime(format_datetime))
