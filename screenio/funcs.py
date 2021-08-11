from time import sleep
from pathlib import Path
from logging import getLogger
from PIL.ImageGrab import grab

logger = getLogger(__name__)


def record(size=(0, 0, 1920, 1080), dt=1, output='frames'):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    counter = len(list(output.iterdir()))
    logger.info('start recording with size=%s, dt=%f, output=%s, counter=%i', size, dt, output, counter)

    current_img = last_img = grab(size)
    while True:
        try:
            current_img = grab(size)
            if current_img != last_img:
                logger.debug('save frame')
                current_img.save(str(output / '{}.jpg'.format(counter)), "JPEG")
                counter += 1
            else:
                logger.debug('skip frame')
            last_img = current_img
            sleep(dt)
        except KeyboardInterrupt:
            break
    logger.info('end recording with counter=%i', counter)
