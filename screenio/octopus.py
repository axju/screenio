import sys
from argparse import ArgumentParser
from logging import getLogger
from time import sleep
from threading import Thread, Event
from pathlib import Path

import toml

from .utils import check_processes, load_func, format_now

logger = getLogger(__name__)


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


def check_trigger(data):
    return check_processes(data)


def octopus(config_file='screenio.toml', dt=10):
    worker = {}
    config = toml.load(config_file)
    logger.debug('config_file="%s", config=%s, worker=%s', config_file, config, worker)
    while True:
        try:
            for key, data in config.items():
                if check_trigger(data):
                    if key not in worker:
                        worker[key] = FuncRunner(
                            data.get('func'),
                            data.get('directory', '.'),
                            data.get('filename', '{}.mp4'),
                            data.get('kwargs', {})
                        )
                elif key in worker:
                    thread = worker.pop(key)
                    thread.stop()
                    logger.debug('worker=%s', worker)
            for _ in range(dt):
                sleep(1)
        except KeyboardInterrupt:
            break

    for thread in worker.values():
        thread.stop()


def main(argv=None):
    parser = ArgumentParser(prog='screenio dynamic')
    parser.add_argument('-c', '--config', default='screenio.toml', help='config file')
    parser.add_argument('-t', '--dt', type=float, default=60, help='delta time default=60')
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    octopus(args.config, args.dt)


if __name__ == '__main__':
    main()
