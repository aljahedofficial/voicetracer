"""
AI Detection Framework

Core 8 metrics for detecting AI-generated text without using large language models.
Optimized for Streamlit deployment.
"""

from .detector import AIDetector
from .preprocessor import TextPreprocessor

__version__ = "1.0.0"
__all__ = ['AIDetector', 'TextPreprocessor']
