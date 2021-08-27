from datetime import datetime, timedelta
from logging import getLogger

from pynput import mouse, keyboard

from watchdog.observers import Observer


from .utils import BasicTrigger, FileSystemHandler, check_processes

logger = getLogger(__name__)


class ProcessesTrigger(BasicTrigger):
    """docstring for ProcessesTrigger."""

    def run(self):
        self.logger.debug('run thread')
        while not self.running.is_set():
            for name, conf in self.config.items():
                self.action(name, check_processes(
                    conf.get('required_proc', []),
                    conf.get('required_proc_files', []),
                    conf.get('banned_proc', []),
                    conf.get('banned_proc_files', []))
                )
            self.wait()


class FileSystemTrigger(BasicTrigger):
    """docstring for ProcessesTrigger."""

    def on_action(self, name, event):
        self.last[name] = datetime.now()
        self.action(name, True)

    def run(self):
        self.logger.debug('run thread')
        self.last = {}
        observer = Observer()
        for name, conf in self.config.items():
            dirname = conf.get('file_system_dir')
            if dirname:
                observer.schedule(FileSystemHandler(name, self.on_action, conf.get('file_system_patterns', ['*.py'])), dirname, recursive=True)
        observer.start()
        try:
            while not self.running.is_set():
                for name, last in self.last.items():
                    if datetime.now() - last > timedelta(seconds=self.config[name].get('file_system_dt', 300)):
                        self.action(name, False)
                self.wait()
        except:
            observer.stop()
            print("Observer Stopped")
        observer.join()


class MouseKeyboardTrigger(BasicTrigger):
    """docstring for MouseKeyboardTrigger."""

    def on_action(self, *args):
        self.last = datetime.now()
        for name in self.config.keys():
            self.action(name, True)

    def run(self):
        self.logger.debug('run thread')
        self.last = datetime.now()
        mouse.Listener(on_move=self.on_action, on_click=self.on_action, on_scroll=self.on_action).start()
        keyboard.Listener(on_press=self.on_action, on_release=self.on_action).start()
        while not self.running.is_set():
            dt = datetime.now() - self.last
            for name, conf in self.config.items():
                if dt > timedelta(seconds=conf.get('mouse_keyboard_dt', 60)):
                    self.action(name, False)
            self.wait()


def on_trigger(sender, name, event):
    print(sender, name, event)


if __name__ == '__main__':
    # trigger = MouseKeyboardTrigger({'test': {'mouse_keyboard_dt': 1}}, on_trigger)
    trigger = ProcessesTrigger({
        'test': {
            'required_proc': ["atom"],
            'required_proc_files': ['/home/axju/projects/socialpy/.git/objects'],
            'banned_proc': ["firefox"],
            'banned_proc_files': ['/home/axju/projects/horn']
        }
    }, on_trigger)
    # trigger = FileSystemTrigger({'test': {'file_system_dir': '/home/axju/projects/screenio', 'file_system_dt': 5}}, on_trigger)
    input('wait')
    trigger.close()
