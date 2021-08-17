from time import sleep
from pathlib import Path
from logging import getLogger


logger = getLogger(__name__)
try:
    import cv2
    import numpy as np
except ImportError:
    logger.info('missing module cv2')
try:
    import ffmpeg
except ImportError:
    logger.info('missing module ffmpeg')
try:
    from PIL.ImageGrab import grab
except ImportError:
    logger.info('missing module pillow')
try:
    from moviepy.editor import ImageSequenceClip
except ImportError:
    logger.info('missing module moviepy')


def record_video_pil(output='out.mp4', size=None, dt=1, framerate=30, difference=True):
    current_img = last_img = grab(size)
    output = Path(output).resolve()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output), fourcc, framerate, current_img.size)
    while True:
        try:
            current_img = grab(size)
            if not difference or current_img != last_img:
                logger.debug('add frame')
                frame = np.array(current_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
            else:
                logger.debug('skip frame')
            last_img = current_img
            sleep(dt)
        except KeyboardInterrupt:
            break
    out.release()


def record_video_ffmpeg(output='out.mp4', filename=':1', f='x11grab', size=(1920, 1080), framerate=1, fps=30, vcodec='libx264', pix_fmt='yuv420p'):
    """
    framerate -> input framrate for recording the screen
    fps -> output framrate for writing the video file
    """
    output = Path(output).resolve()
    logger.info('start ffmpeg recording with:')
    logger.info('size=%s, framerate=%f, output=%s', size, framerate, output)
    logger.info('fps=%s, vcodec=%s, pix_fmt=%s, filename=%s, f=%s', fps, vcodec, pix_fmt, filename, f)

    stream = ffmpeg.input(filename=filename, f=f, framerate=framerate, video_size=size).setpts('N/TB/{}'.format(fps))
    stream = ffmpeg.output(stream, str(output), vcodec=vcodec, preset='ultrafast', r=fps, pix_fmt=pix_fmt)
    process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
    try:
        input('')
    except KeyboardInterrupt:
        logger.info('breack with KeyboardInterrupt')
    finally:
        process.communicate(input=b"q")
        logger.info('end ffmpeg recording')


def record_frames_pil(output='frames', size=(0, 0, 1920, 1080), dt=1, difference=True):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    counter = len(list(output.iterdir()))
    logger.info('start pillow recording with size=%s, dt=%f, output=%s, counter=%i', size, dt, output, counter)

    current_img = last_img = grab(size)
    while True:
        try:
            current_img = grab(size)
            if not difference or current_img != last_img:
                logger.debug('save frame')
                current_img.save(str(output / '{:06d}.png'.format(counter)))
                counter += 1
            else:
                logger.debug('skip frame')
            last_img = current_img
            sleep(dt)
        except KeyboardInterrupt:
            break
    logger.info('end pillow recording with counter=%i', counter)


def record_frames_ffmpeg(output='frames', size=(1920, 1080), framerate=1, filename=':1', f='x11grab'):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    counter = len(list(output.iterdir()))
    logger.info('start ffmpeg recording with size=%s, framerate=%f, output=%s, counter=%i', size, framerate, output, counter)

    stream = ffmpeg.input(filename=filename, f=f, video_size=size, framerate=framerate)
    stream = ffmpeg.output(stream, str(output / '%06d.png'), start_number=counter, r=1)
    process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
    try:
        input('')
    except KeyboardInterrupt:
        logger.info('breack with KeyboardInterrupt')
    finally:
        process.communicate(input=b"q")
        counter = len(list(output.iterdir())) - 1
        logger.info('end ffmpeg recording with counter=%i', counter)


def frames_to_video_moviepy(directory='frames', output='out.mp4', fps=30):
    directory = Path(directory).resolve()
    logger.debug('directory=%s', directory)
    files = [str(file) for file in directory.iterdir()]
    files.sort()
    clip = ImageSequenceClip(files, fps=fps)
    clip.write_videofile(str(output))


def frames_to_video_ffmpeg(directory='frames', output='out.mp4', fps=30, vcodec='libx264', pix_fmt='yuv420p'):
    directory = Path(directory).resolve()
    filename = str(directory / '%06d.png')
    stream = ffmpeg.input(filename=filename, f='image2').setpts('N/TB/{}'.format(fps))
    stream = ffmpeg.output(stream, output, vcodec=vcodec, pix_fmt=pix_fmt, r=fps)
    ffmpeg.run(stream, overwrite_output=True)
