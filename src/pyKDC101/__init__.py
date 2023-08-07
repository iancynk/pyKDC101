"""pyKDC101 - Python wrapper to control TL KDC101 controllers"""

import pkg_resources

from .core import KDC

__version__ = pkg_resources.require("pyKDC101")[0].version
__author__ = "iancynk <ian.cynk@posteo.eu>"
__all__ = ['KDC']