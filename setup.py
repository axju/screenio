import os
from pathlib import Path
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(Path(__file__).resolve().parent)

setup(
    packages=['screenio'],
    include_package_data=True,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'importlib-metadata; python_version < "3.8.0"',
        'dynaconf',
        'pillow',
        'moviepy',
        'ffmpeg-python',
        'opencv-python',
    ],
    entry_points={
        'console_scripts': [
            'screenio=screenio.cli:main',
        ],
        'screenio.register_cmd': [
            'record=screenio.funcs:record_cli',
            'convert=screenio.funcs:convert_cli',
        ],
    }
)
