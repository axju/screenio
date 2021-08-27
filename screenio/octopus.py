import sys
from argparse import ArgumentParser
from logging import getLogger
from time import sleep

import toml

from .utils import FuncRunner, check_triggers
from .triggers import ProcessesTrigger, FileSystemTrigger, MouseKeyboardTrigger

logger = getLogger(__name__)


class Octopus:
    """docstring for Octopus."""
    trigger_cls = [
        MouseKeyboardTrigger,
        ProcessesTrigger,
        FileSystemTrigger,
    ]

    def __init__(self, config='screenio.toml', dt=60):
        super(Octopus, self).__init__()
        self.config = toml.load(config)
        default = self.config.pop('default', {})
        for data in self.config.values():
            for key, value in default.items():
                data.setdefault(key, value)
        for key, value in self.config.items():
            logger.debug('name=%s data=%s', key, value)
        self.dt, self.worker, self.trigger = dt, {}, {}
        self.triggers = [cls(self.config, self.on_trigger) for cls in self.trigger_cls]

    def on_trigger(self, sender, name, event):
        trigger = self.trigger.get(name, [])
        if event and sender not in trigger:
            trigger.append(sender)
            if check_triggers(trigger, self.config[name].get('triggers', [])) and name not in self.worker:
                self.worker[name] = FuncRunner(
                    self.config[name].get('func'),
                    self.config[name].get('directory', '.'),
                    self.config[name].get('filename', '{}.mp4'),
                    self.config[name].get('kwargs', {})
                )
        elif not event and sender in trigger:
            trigger.remove(sender)
            if not check_triggers(trigger, self.config[name].get('triggers', [])) and name in self.worker:
                thread = self.worker.pop(name)
                thread.stop()

        self.trigger[name] = trigger

    def on_trigger_mouse(self, name, event):
        self.on_trigger('mouse', name, event)

    def wait(self):
        while True:
            try:
                logger.debug('current trigger %s', self.trigger)
                for _ in range(self.dt):
                    sleep(1)
            except KeyboardInterrupt:
                break
        for trigger in self.triggers:
            trigger.close()
        for thread in self.worker.values():
            thread.stop()
            thread.join()


def main(argv=None):
    parser = ArgumentParser(prog='screenio dynamic')
    parser.add_argument('-c', '--config', default='screenio.toml', help='config file')
    parser.add_argument('-t', '--dt', type=int, default=60, help='delta time default=60')
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    octopus = Octopus(args.config, args.dt)
    octopus.wait()


if __name__ == '__main__':
    main()
