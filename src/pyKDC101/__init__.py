"""pyKDC101 - Python wrapper to control TL KDC101 controllers"""

import pkg_resources
__version__ = pkg_resources.require("pyKDC101")[0].version
__author__ = "iancynk <ian.cynk@posteo.eu>"
__all__ = ['KDC']

from .core import KDC
