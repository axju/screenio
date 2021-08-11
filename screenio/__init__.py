"""Top-level package for screenio"""
try:
    from importlib.metadata import version, PackageNotFoundError
except ModuleNotFoundError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version('screenio')
except PackageNotFoundError:
    __version__ = 'unknown'
finally:
    del version, PackageNotFoundError
