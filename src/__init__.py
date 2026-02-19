"""
nuts_vision - Electronic Component Detection

A computer vision system for automated electronic circuit board analysis.
"""

__version__ = "2.0.0"
__author__ = "nuts_vision contributors"

from .detect import ComponentDetector
from .crop import ComponentCropper
from .visualize import DetectionVisualizer

__all__ = [
    'ComponentDetector',
    'ComponentCropper',
    'DetectionVisualizer'
]
