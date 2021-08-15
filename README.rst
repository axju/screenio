========
ScreenIO
========
Screen recorder to create time lapse videos.

Install
-------
::

  pip install screenio

Commands
--------
::

  screenio record -o out.mp4

Development
-----------
Some information for crazy developers. Virtual environment windows::

  python -m venv venv
  venv\Scripts\activate

Virtual environment linux::

  python3 -m venv venv
  source venv/bin/activate

Setup project::

  python -m pip install --upgrade pip wheel setuptools twine tox flake8 pylint pylama
  pip install -e .

Run some test::

  tox

Create package::

  python setup.py sdist bdist_wheel

Upload package::

  twine upload dist/*

Run it on Termux::

  pkg install clang # for cryptography
  ./dev.sh
