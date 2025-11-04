# read and set version from main pyproject.toml
from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"
