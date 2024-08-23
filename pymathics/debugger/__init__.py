"""
Mathics3 Debugger
"""

from pymathics.debugger.__main__ import DebugActivate, Debugger, TraceActivate
from pymathics.debugger.version import __version__

pymathics_version_data = {
    "author": "The Mathics3 Team",
    "version": __version__,
    "name": "Debugger",
    "requires": [],
}


# These are the publicly exported names
__all__ = [
    "DebugActivate",
    "Debugger",
    "TraceActivate",
    "pymathics_version_data",
]
