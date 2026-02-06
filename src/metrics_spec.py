"""
VoiceTracer Metric Definitions & Formulas

Defines how each metric is calculated, normalized, and interpreted.
Reference: "The Monolingualism of the Machine" thesis methodology.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import math


class MetricType(Enum):
    """Types of metrics in VoiceTracer."""
    BURSTINESS = "burstiness"
    LEXICAL_DIVERSITY = "lexical_diversity"
    SYNTACTIC_COMPLEXITY = "syntactic_complexity"
    AI_ISM_LIKELIHOOD = "ai_ism_likelihood"
    FUNCTION_WORD_RATIO = "function_word_ratio"
    DISCOURSE_MARKER_DENSITY = "discourse_marker_density"
    INFORMATION_DENSITY = "information_density"
    EPISTEMIC_HEDGING = "epistemic_hedging"


@dataclass
class MetricDefinition:
    """Specification for a metric."""
    metric_type: MetricType
    name: str
    short_description: str
    long_description: str
    formula: str
    range_min: float
    range_max: float
    optimal_value: float
    interpretation_low: str
    interpretation_high: str
    thesis_relevance: str


# ============================================================================
# METRIC 1: BURSTINESS INDEX
# ============================================================================
BURSTINESS_DEFINITION = MetricDefinition(
    metric_type=MetricType.BURSTINESS,
    name="Burstiness Index",
    short_description="Sentence length variation (SD / mean)",
    long_description="""
    Measures the variation in sentence lengths throughout the text.
    
    Formula: Standard Deviation of sentence lengths / Mean sentence length
    
    Calculation Steps:
    1. Extract all sentences from text
    2. Count words in each sentence
    3. Calculate mean sentence length
    4. Calculate standard deviation of sentence lengths
    5. Divide SD by mean (coefficient of variation)
    """,
    formula="σ(sentence_lengths) / μ(sentence_lengths)",
    range_min=0.0,
    range_max=3.0,
    optimal_value=1.3,  # Human-like variation
    interpretation_low="Machine-like uniformity; suggests AI editing standardized lengths",
    interpretation_high="Human-like variation; indicates authentic, natural writing",
    thesis_relevance="""
    AI models optimize for readability and consistency, standardizing sentence lengths.
    Human writers naturally vary sentence structures for emphasis and flow.
    This metric directly measures homogenization of sentence-level style.
    """
)


# ============================================================================
# METRIC 2: LEXICAL DIVERSITY
# ============================================================================
LEXICAL_DIVERSITY_DEFINITION = MetricDefinition(
    metric_type=MetricType.LEXICAL_DIVERSITY,
    name="Lexical Diversity",
    short_description="Vocabulary richness (TTR or MTLD)",
    long_description="""
    Measures vocabulary richness and diversity.
    
    Method 1 - Type-Token Ratio (TTR):
    Formula: Unique words / Total words
    
    Method 2 - MTLD (Mean Segmental Type-Token Ratio):
    More robust to text length variations
    Segments text and averages TTR across segments
    
    For VoiceTracer, we use MTLD normalized 0-1:
    MTLD_normalized = (MTLD - 70) / 110  (capped at 1.0)
    
    Interpretation:
    - < 0.4: Low diversity (formulaic, repetitive)
    - 0.4-0.6: Moderate diversity
    - > 0.6: High diversity (varied vocabulary)
    """,
    formula="MTLD_normalized = (MTLD - 70) / 110",
    range_min=0.0,
    range_max=1.0,
    optimal_value=0.65,  # Human-like vocabulary richness
    interpretation_low="Formulaic vocabulary; suggests AI standardization of word choice",
    interpretation_high="Rich vocabulary; indicates authentic, varied expression",
    thesis_relevance="""
    AI models rely on common academic phrases and formulaic expressions.
    Human L2 writers use more diverse (even if occasionally awkward) vocabulary.
    Vocabulary flattening is a key indicator of stylistic homogenization.
    """
)


# ============================================================================
# METRIC 3: SYNTACTIC COMPLEXITY
# ============================================================================
SYNTACTIC_COMPLEXITY_DEFINITION = MetricDefinition(
    metric_type=MetricType.SYNTACTIC_COMPLEXITY,
    name="Syntactic Complexity",
    short_description="Sentence structure diversity (words/sent, subordination, modifiers)",
    long_description="""
    Composite metric measuring structural complexity across 3 dimensions:
    
    1. Average Sentence Length (ASL)
       Formula: Total words / Number of sentences
       Typical range: 15-25 words
    
    2. Subordination Ratio
       Formula: Subordinate clauses / Total clauses
       Measures use of dependent clauses (because, when, which, etc.)
       Range: 0-1 (higher = more complex)
    
    3. Modifier Density
       Formula: Modifying phrases & adjectives / Total tokens
       Measures descriptive complexity
       Range: 0-1 (higher = more modified)
    
    Composite Score:
    SC = (ASL_norm × 0.4) + (Sub_ratio × 0.3) + (Mod_density × 0.3)
    Where norm scores are scaled to 0-1 range
    
    Interpretation:
    - High complexity: Varied sentence structures, sophisticated syntax
    - Low complexity: Simple, repetitive sentence patterns
    """,
    formula="SC = (ASL_norm × 0.4) + (Sub_ratio × 0.3) + (Mod_density × 0.3)",
    range_min=0.0,
    range_max=1.0,
    optimal_value=0.65,  # Balanced complexity
    interpretation_low="Simple structures; suggests AI simplification for clarity",
    interpretation_high="Complex structures; indicates authentic, sophisticated syntax",
    thesis_relevance="""
    AI editing often simplifies sentence structures and reduces clause complexity.
    Authentic L2 writing contains more structural variety (including mistakes).
    Syntactic flattening is another key marker of homogenization.
    """
)


# ============================================================================
# METRIC 4: AI-ISM LIKELIHOOD (PATTERN DETECTION)
# ============================================================================
AI_ISM_DEFINITION = MetricDefinition(
    metric_type=MetricType.AI_ISM_LIKELIHOOD,
    name="AI-ism Likelihood",
    short_description="Frequency of AI-characteristic phrases and patterns",
    long_description="""
    Detects formulaic phrases and patterns characteristic of AI-generated text.
    
    Categorized AI-isms:
    
    1. OPENING HEDGES (0-30 points)
       - "It is important to note that..."
       - "It should be noted that..."
       - "It is widely recognized that..."
       - Detection: Regex + frequency
    
    2. CLOSING/TRANSITION PHRASES (0-30 points)
       - "In conclusion..."
       - "To summarize..."
       - "It is therefore clear that..."
       - "In light of the above..."
    
    3. FORMULAIC CONNECTORS (0-20 points)
       - "delve into", "shed light on", "pave the way"
       - "leverage", "in the context of", "moreover"
       - Rare in authentic L2 writing
    
    4. REPETITIVE PATTERNS (0-20 points)
       - Repeated n-grams (bigrams appearing >3x)
       - Passive voice ratio > 25%
       - Unusual punctuation uniformity
    
    Total Score: 0-100 (normalized)
    - 0-20: Likely human writing
    - 20-50: Mixed human/AI characteristics
    - 50-80: Possibly AI-edited
    - 80-100: Likely AI-generated
    """,
    formula="AI-ism = (openings + closings + connectors + patterns) / 4",
    range_min=0.0,
    range_max=100.0,
    optimal_value=15.0,  # Low score indicates human writing
    interpretation_low="Human-like characteristics; natural expression",
    interpretation_high="AI-like characteristics; formulaic patterns detected",
    thesis_relevance="""
    AI models generate text from patterns learned in training data.
    This creates recognizable stylistic fingerprints (formulaic phrases).
    Documenting AI-ism frequency shows how AI-editing introduces artificiality.
    """
)


# ==========================================================================
# METRIC 5: FUNCTION WORD RATIO
# ==========================================================================
FUNCTION_WORD_RATIO_DEFINITION = MetricDefinition(
    metric_type=MetricType.FUNCTION_WORD_RATIO,
    name="Function Word Ratio",
    short_description="Ratio of grammatical scaffolding words",
    long_description="""
    Measures the proportion of function words (articles, prepositions, pronouns,
    auxiliaries, conjunctions) relative to total words.
    AI writing often has higher function word ratios due to over-scaffolded syntax.
    """,
    formula="function_words / total_words",
    range_min=0.0,
    range_max=1.0,
    optimal_value=0.52,
    interpretation_low="Content-heavy wording; more human-like efficiency",
    interpretation_high="Over-scaffolded syntax; more AI-like",
    thesis_relevance="""
    AI systems favor safe, grammatical scaffolding, increasing function words.
    Human writers rely more on content words and varied phrasing.
    """,
)


# ==========================================================================
# METRIC 6: DISCOURSE MARKER DENSITY
# ==========================================================================
DISCOURSE_MARKER_DENSITY_DEFINITION = MetricDefinition(
    metric_type=MetricType.DISCOURSE_MARKER_DENSITY,
    name="Discourse Marker Density",
    short_description="Frequency of explicit logical connectors",
    long_description="""
    Measures the density of discourse markers (moreover, therefore, in conclusion)
    per 1,000 words. AI writing tends to over-signpost structure.
    """,
    formula="(discourse_markers / total_words) * 1000",
    range_min=0.0,
    range_max=50.0,
    optimal_value=10.0,
    interpretation_low="Implicit flow; more human-like",
    interpretation_high="Over-signposted structure; more AI-like",
    thesis_relevance="""
    AI outputs rely on explicit connectors to maintain coherence,
    increasing discourse marker density.
    """,
)


# ==========================================================================
# METRIC 7: INFORMATION DENSITY
# ==========================================================================
INFORMATION_DENSITY_DEFINITION = MetricDefinition(
    metric_type=MetricType.INFORMATION_DENSITY,
    name="Information Density",
    short_description="Specific content per word",
    long_description="""
    Estimates how much concrete information appears relative to word count.
    Combines content-word ratio, unique content ratio, and proper noun density.
    Low density suggests verbose, generic text typical of AI.
    """,
    formula="(content_ratio * 0.5) + (unique_content_ratio * 0.3) + (proper_noun_density * 0.2)",
    range_min=0.0,
    range_max=1.0,
    optimal_value=0.60,
    interpretation_low="Verbose, low-specificity text; more AI-like",
    interpretation_high="Concrete, efficient wording; more human-like",
    thesis_relevance="""
    AI tends to expand with generic filler. Human writing is denser with concrete
    details and distinct content words.
    """,
)


# ==========================================================================
# METRIC 8: EPISTEMIC HEDGING INDEX
# ==========================================================================
EPISTEMIC_HEDGING_DEFINITION = MetricDefinition(
    metric_type=MetricType.EPISTEMIC_HEDGING,
    name="Epistemic Hedging Index",
    short_description="Markers of uncertainty and humility",
    long_description="""
    Measures the frequency of hedging and uncertainty markers. Human writers
    often hedge claims; AI text can be overconfident and under-hedged.
    """,
    formula="(hedges + qualifiers) / total_words",
    range_min=0.0,
    range_max=0.20,
    optimal_value=0.10,
    interpretation_low="Overconfident phrasing; more AI-like",
    interpretation_high="Hedged, nuanced phrasing; more human-like",
    thesis_relevance="""
    AI outputs often sound overly certain. Hedging frequency is a strong indicator
    of authentic human reasoning in academic writing.
    """,
)


# ============================================================================
# AI-ISM PHRASE DATABASE
# ============================================================================
AI_ISM_PHRASES = {
    "opening": [
        "it is important to note that",
        "it should be noted that",
        "it is widely recognized that",
        "it is evident that",
        "it is clear that",
        "one could argue that",
        "one might suggest that",
        "furthermore, it is",
    ],
    "closing": [
        "in conclusion",
        "to summarize",
        "in summary",
        "to conclude",
        "ultimately",
        "in essence",
        "it is therefore clear",
        "in light of the above",
    ],
    "connector": [
        "delve into",
        "shed light on",
        "pave the way",
        "leverage",
        "in the context of",
        "moreover",
        "furthermore",
        "in the interest of",
        "in order to",
        "so as to",
        "with respect to",
        "as a matter of fact",
    ],
    "passive": [
        "can be seen",
        "is considered",
        "is known",
        "is thought",
        "is believed",
        "is said to",
        "is noted",
        "is suggested",
    ],
}


# ==========================================================================
# LEXICONS FOR NEW METRICS
# ==========================================================================
FUNCTION_WORDS = {
    "a", "an", "the", "and", "or", "but", "nor", "for", "so", "yet",
    "in", "on", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "out", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "can", "will", "just", "don", "should", "now",
    "is", "are", "was", "were", "be", "been", "being", "am",
    "do", "does", "did", "have", "has", "had", "having",
    "i", "me", "my", "mine", "we", "us", "our", "ours", "you", "your",
    "yours", "he", "him", "his", "she", "her", "hers", "it", "its",
    "they", "them", "their", "theirs", "this", "that", "these", "those",
    "if", "because", "while", "although", "though", "since", "unless",
    "as", "until", "whether", "than",
}

DISCOURSE_MARKERS = {
    "moreover", "therefore", "however", "furthermore", "consequently", "thus",
    "in conclusion", "on the other hand", "for instance", "for example",
    "in addition", "as a result", "in contrast", "in summary", "to conclude",
    "additionally", "meanwhile", "subsequently", "nevertheless", "nonetheless",
    "indeed", "in other words", "by contrast", "as such", "overall",
}

HEDGING_MARKERS = {
    "perhaps", "arguably", "possibly", "probably", "likely", "unlikely",
    "it seems", "it appears", "suggests", "may", "might", "could",
    "tends to", "in my view", "i think", "i believe", "one could argue",
    "it is possible", "it is plausible",
}

CONFIDENCE_MARKERS = {
    "certainly", "definitely", "absolutely", "undoubtedly", "clearly",
    "obviously", "without doubt", "must be", "is clear that",
}

QUALIFICATION_MARKERS = {
    "however", "although", "though", "yet", "still", "but", "while",
    "nevertheless", "nonetheless",
}


# ============================================================================
# METRIC NORMALIZATION RULES
# ============================================================================
def normalize_metric(metric_value: float, metric_type: MetricType) -> float:
    """
    Normalize metric value to 0-1 scale for consistent display.
    
    Args:
        metric_value: Raw metric value
        metric_type: Type of metric
    
    Returns:
        Normalized value 0-1 (capped)
    """
    if metric_type == MetricType.BURSTINESS:
        # Burstiness: 0-3 → 0-1
        # 0.5 = very low, 1.5 = optimal, 3.0 = very high
        return min(metric_value / 3.0, 1.0)
    
    elif metric_type == MetricType.LEXICAL_DIVERSITY:
        # Already normalized 0-1
        return min(metric_value, 1.0)
    
    elif metric_type == MetricType.SYNTACTIC_COMPLEXITY:
        # Already normalized 0-1
        return min(metric_value, 1.0)
    
    elif metric_type == MetricType.AI_ISM_LIKELIHOOD:
        # AI-ism: 0-100 → 0-1
        # But invert interpretation (high = bad)
        raw_norm = min(metric_value / 100.0, 1.0)
        return 1.0 - raw_norm  # Invert: high AI-ism = low human-ness

    elif metric_type == MetricType.FUNCTION_WORD_RATIO:
        # 0.45-0.65 is typical; higher is more AI-like
        normalized = (metric_value - 0.45) / 0.20
        return max(0.0, min(normalized, 1.0))

    elif metric_type == MetricType.DISCOURSE_MARKER_DENSITY:
        # Per 1000 words, cap at 30
        return min(metric_value / 30.0, 1.0)

    elif metric_type == MetricType.INFORMATION_DENSITY:
        # Already 0-1, but invert so lower density = more AI-like
        return 1.0 - min(metric_value, 1.0)

    elif metric_type == MetricType.EPISTEMIC_HEDGING:
        # Hedge rate 0-0.15; lower hedging = more AI-like
        normalized = (0.15 - metric_value) / 0.12
        return max(0.0, min(normalized, 1.0))
    
    return metric_value


def interpret_metric(metric_value: float, metric_type: MetricType) -> Dict[str, str]:
    """
    Generate human-readable interpretation of a metric.
    
    Returns dict with 'level' (low/medium/high) and 'interpretation' text.
    """
    norm = normalize_metric(metric_value, metric_type)
    
    if norm < 0.33:
        level = "low"
    elif norm < 0.67:
        level = "medium"
    else:
        level = "high"
    
    # Return interpretation based on metric type
    interpretations = {
        MetricType.BURSTINESS: {
            "low": "Machine-like uniformity",
            "medium": "Moderate variation",
            "high": "Human-like natural variation"
        },
        MetricType.LEXICAL_DIVERSITY: {
            "low": "Formulaic, repetitive vocabulary",
            "medium": "Moderate vocabulary richness",
            "high": "Rich, varied vocabulary"
        },
        MetricType.SYNTACTIC_COMPLEXITY: {
            "low": "Simple, repetitive structures",
            "medium": "Moderate complexity",
            "high": "Complex, varied structures"
        },
        MetricType.AI_ISM_LIKELIHOOD: {
            "low": "Natural human-like patterns",
            "medium": "Mixed characteristics",
            "high": "Formulaic AI-like patterns"
        },
        MetricType.FUNCTION_WORD_RATIO: {
            "low": "Content-heavy wording",
            "medium": "Balanced scaffolding",
            "high": "Over-scaffolded syntax"
        },
        MetricType.DISCOURSE_MARKER_DENSITY: {
            "low": "Implicit flow",
            "medium": "Balanced signposting",
            "high": "Over-signposted structure"
        },
        MetricType.INFORMATION_DENSITY: {
            "low": "Verbose, generic wording",
            "medium": "Moderate specificity",
            "high": "Dense, concrete content"
        },
        MetricType.EPISTEMIC_HEDGING: {
            "low": "Overconfident tone",
            "medium": "Moderately hedged",
            "high": "Nuanced, hedged tone"
        }
    }
    
    return {
        "level": level,
        "interpretation": interpretations[metric_type].get(level, "Unknown")
    }


# ============================================================================
# INTERPRETATION GUIDES
# ============================================================================
METRIC_NARRATIVES = {
    MetricType.BURSTINESS: {
        "what_is_it": (
            "Burstiness measures how much your sentence lengths vary. "
            "A high burstiness means you write sentences of very different lengths "
            "(some short, some long). A low burstiness means your sentences are "
            "all similar lengths."
        ),
        "why_matters": (
            "AI models optimize for readability by making sentence lengths uniform. "
            "Human writers naturally vary their sentence lengths for emphasis and flow. "
            "Drop in burstiness indicates AI editing standardized your writing."
        ),
        "why_changed": (
            "AI editors often restructure complex sentences into shorter, simpler ones, "
            "which reduces the natural variation in your sentence lengths."
        ),
        "recommendation": (
            "Review the edited sentences. Consider keeping some of your original "
            "longer or more complex constructions while accepting AI improvements "
            "for clarity."
        ),
    },
    MetricType.LEXICAL_DIVERSITY: {
        "what_is_it": (
            "Lexical diversity measures how many different words you use relative "
            "to total words. Higher diversity means richer vocabulary; lower means "
            "you repeat words or use formulaic phrases."
        ),
        "why_matters": (
            "AI models draw from common academic phrases and avoid less frequent words. "
            "Your authentic writing, even with mistakes, uses a wider range of vocabulary. "
            "Drop in diversity indicates AI introduced formulaic language."
        ),
        "why_changed": (
            "AI editing replaces varied (but potentially awkward) word choices with "
            "common, 'safe' alternatives from training data."
        ),
        "recommendation": (
            "Keep some of your original less-common word choices if they are accurate. "
            "They demonstrate your authentic voice and vocabulary growth."
        ),
    },
    MetricType.SYNTACTIC_COMPLEXITY: {
        "what_is_it": (
            "Syntactic complexity measures the sophistication of your sentence structures. "
            "It includes sentence length, use of dependent clauses, and descriptive phrases."
        ),
        "why_matters": (
            "AI simplifies syntax for clarity, often removing complex (and authentic) "
            "sentence structures. Your original writing shows your actual linguistic level."
        ),
        "why_changed": (
            "AI editors break complex sentences into simpler ones and remove modifiers "
            "that don't directly aid clarity."
        ),
        "recommendation": (
            "Review AI simplifications. Keep complex structures that were grammatically "
            "correct; they show your advancing syntax skills."
        ),
    },
    MetricType.AI_ISM_LIKELIHOOD: {
        "what_is_it": (
            "AI-ism likelihood detects phrases and patterns typical of AI-generated text. "
            "Common AI phrases include 'it is important to note that', 'delve into', "
            "'in light of', and repetitive structures."
        ),
        "why_matters": (
            "High AI-ism score indicates the text relies on AI-generated patterns, "
            "not your authentic voice. Readers (including plagiarism detection systems) "
            "may notice the shift."
        ),
        "why_changed": (
            "AI editing replaced your original phrasing with formulaic alternatives "
            "from its training data."
        ),
        "recommendation": (
            "Revert some AI suggestions in favor of your original phrasing, especially "
            "opening and closing sentences where your voice matters most."
        ),
    },
    MetricType.FUNCTION_WORD_RATIO: {
        "what_is_it": (
            "Function word ratio measures how much grammatical scaffolding (articles, "
            "prepositions, pronouns) appears in your text."
        ),
        "why_matters": (
            "AI editing often increases function words to smooth grammar and flow, "
            "which can make writing feel more uniform and less content-dense."
        ),
        "why_changed": (
            "Edits that add connectors, articles, and auxiliaries raise the ratio and "
            "signal more formulaic phrasing."
        ),
        "recommendation": (
            "Tighten sentences where possible and keep your original content-heavy wording "
            "when it remains clear and correct."
        ),
    },
    MetricType.DISCOURSE_MARKER_DENSITY: {
        "what_is_it": (
            "Discourse marker density counts explicit connectors like 'moreover' and "
            "'therefore' per 1,000 words."
        ),
        "why_matters": (
            "AI outputs often over-signpost arguments, which can make the text feel "
            "formulaic or overly guided."
        ),
        "why_changed": (
            "When AI inserts extra transitions to structure ideas, density rises and "
            "the flow becomes more explicit."
        ),
        "recommendation": (
            "Remove repeated connectors and rely on paragraph structure to convey flow."
        ),
    },
    MetricType.INFORMATION_DENSITY: {
        "what_is_it": (
            "Information density estimates how much concrete content appears per word, "
            "based on content words and proper noun signals."
        ),
        "why_matters": (
            "AI edits can expand text with generic phrasing, reducing specificity and "
            "making writing feel less focused."
        ),
        "why_changed": (
            "Generic expansions and paraphrases dilute concrete details, lowering density."
        ),
        "recommendation": (
            "Reintroduce specific facts, names, or precise terminology where appropriate."
        ),
    },
    MetricType.EPISTEMIC_HEDGING: {
        "what_is_it": (
            "Epistemic hedging tracks uncertainty markers (e.g., 'might', 'perhaps') that "
            "signal nuanced academic caution."
        ),
        "why_matters": (
            "Human academic writing often hedges claims. AI edits can sound more certain, "
            "which flattens nuance."
        ),
        "why_changed": (
            "Overconfident revisions reduce hedging and shift tone toward certainty."
        ),
        "recommendation": (
            "Restore hedging where claims are probabilistic or still under debate."
        ),
    },
}
