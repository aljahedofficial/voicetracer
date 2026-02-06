"""
AI Detection Metrics Module

Contains implementations of the Core 8 metrics.
"""

from .burstiness import calculate_burstiness
from .lexical_diversity import calculate_lexical_diversity
from .discourse_markers import calculate_discourse_markers
from .function_words import calculate_function_word_ratio
from .epistemic_hedging import calculate_epistemic_hedging
from .syntax_depth import calculate_syntax_depth
from .information_density import calculate_information_density
from .register_stability import calculate_register_stability

__all__ = [
    'calculate_burstiness',
    'calculate_lexical_diversity',
    'calculate_discourse_markers',
    'calculate_function_word_ratio',
    'calculate_epistemic_hedging',
    'calculate_syntax_depth',
    'calculate_information_density',
    'calculate_register_stability'
]
