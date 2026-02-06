"""
VoiceTracer Data Models

Defines core entities for document analysis, metrics, and sessions.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import uuid4
import json


@dataclass
class TextMetadata:
    """Metadata about a text."""
    word_count: int
    char_count: int
    sentence_count: int
    token_count: int
    avg_sentence_length: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MetricScores:
    """Individual metric scores."""
    burstiness: float
    lexical_diversity: float
    syntactic_complexity: float
    ai_ism_likelihood: float
    function_word_ratio: float
    discourse_marker_density: float
    information_density: float
    epistemic_hedging: float


@dataclass
class MetricDeltas:
    """Changes between original and edited metrics."""
    burstiness_delta: float
    burstiness_pct_change: float
    lexical_diversity_delta: float
    lexical_diversity_pct_change: float
    syntactic_complexity_delta: float
    syntactic_complexity_pct_change: float
    ai_ism_delta: float
    ai_ism_pct_change: float
    function_word_ratio_delta: float
    function_word_ratio_pct_change: float
    discourse_marker_density_delta: float
    discourse_marker_density_pct_change: float
    information_density_delta: float
    information_density_pct_change: float
    epistemic_hedging_delta: float
    epistemic_hedging_pct_change: float


@dataclass
class AIismCategory:
    """Category of AI-ism phrases."""
    category: str  # 'opening', 'closing', 'connector', 'transition'
    phrase: str
    occurrence_count: int
    likelihood: float  # 0-100
    example_context: Optional[str] = None


@dataclass
class DocumentPair:
    """A pair of original and AI-edited documents."""
    id: str = field(default_factory=lambda: str(uuid4()))
    original_text: str = ""
    edited_text: str = ""
    original_metadata: Optional[TextMetadata] = None
    edited_metadata: Optional[TextMetadata] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.original_metadata:
            data['original_metadata'] = asdict(self.original_metadata)
            data['original_metadata']['created_at'] = self.original_metadata.created_at.isoformat()
        if self.edited_metadata:
            data['edited_metadata'] = asdict(self.edited_metadata)
            data['edited_metadata']['created_at'] = self.edited_metadata.created_at.isoformat()
        return data


@dataclass
class AnalysisResult:
    """Complete analysis result for a document pair."""
    doc_pair_id: str
    original_metrics: MetricScores
    edited_metrics: MetricScores
    metric_deltas: MetricDeltas
    ai_isms: List[AIismCategory] = field(default_factory=list)
    benchmark_comparisons: Dict[str, Dict[str, float]] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.now)
    method_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            'doc_pair_id': self.doc_pair_id,
            'original_metrics': asdict(self.original_metrics),
            'edited_metrics': asdict(self.edited_metrics),
            'metric_deltas': asdict(self.metric_deltas),
            'ai_isms': [asdict(ai) for ai in self.ai_isms],
            'benchmark_comparisons': self.benchmark_comparisons,
            'calculated_at': self.calculated_at.isoformat(),
            'method_version': self.method_version,
        }


@dataclass
class Benchmark:
    """Benchmark baseline for metric comparison."""
    name: str
    burstiness: float
    lexical_diversity: float
    syntactic_complexity: float
    ai_ism_likelihood: float
    function_word_ratio: float
    discourse_marker_density: float
    information_density: float
    epistemic_hedging: float
    description: str = ""
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Session:
    """User session for tracking analysis work."""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    document_pairs: List[str] = field(default_factory=list)  # List of doc_pair_ids
    analysis_results: List[str] = field(default_factory=list)  # List of result IDs
    auto_save_interval: int = 30  # seconds
    last_activity: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_activity'] = self.last_activity.isoformat()
        data['created_at'] = self.created_at.isoformat()
        return data


# Metric baseline benchmarks (from thesis data + research)
DEFAULT_BENCHMARKS = [
    Benchmark(
        name="L2 Native Speaker",
        burstiness=1.45,
        lexical_diversity=0.68,
        syntactic_complexity=18.5,
        ai_ism_likelihood=5.2,
        function_word_ratio=0.52,
        discourse_marker_density=9.0,
        information_density=0.62,
        epistemic_hedging=0.11,
        description="Baseline from native English speakers",
        source="Agarwal et al. 2024"
    ),
    Benchmark(
        name="L2 Unassisted Writing",
        burstiness=1.23,
        lexical_diversity=0.55,
        syntactic_complexity=16.2,
        ai_ism_likelihood=3.1,
        function_word_ratio=0.50,
        discourse_marker_density=8.0,
        information_density=0.58,
        epistemic_hedging=0.09,
        description="L2 learner writing without AI assistance",
        source="VoiceTracer Study"
    ),
    Benchmark(
        name="AI-Edited Text (ChatGPT)",
        burstiness=0.78,
        lexical_diversity=0.42,
        syntactic_complexity=19.3,
        ai_ism_likelihood=78.5,
        function_word_ratio=0.60,
        discourse_marker_density=18.0,
        information_density=0.42,
        epistemic_hedging=0.04,
        description="Text edited by ChatGPT with 'grammar only' prompt",
        source="VoiceTracer Study"
    ),
]
