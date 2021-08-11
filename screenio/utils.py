import logging
from pkg_resources import iter_entry_points
from dynaconf import Dynaconf


def load_settings(path=None):
    settings_files = ['settings.toml']
    if path:
        settings_files += [path]
    return Dynaconf(settings_files=settings_files)


def setup_logger(level=0, logger=''):
    """setup the root logger"""
    logger = logging.getLogger(logger)
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, level or 0)]
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)


def load_entry_points():
    """get all entry points"""
    return {enp.name: enp.load() for enp in iter_entry_points(group='screenio.register_cmd')}
