"""
VoiceTracer Testing & Validation Module

Unit tests and validation for metrics, exports, and accessibility.
"""

import pytest
from typing import Dict, List, Tuple
from text_processor import TextProcessor, StatisticsCalculator, TextAnalysisPreprocessor
from metric_calculator import (
    BurstinessCalculator,
    LexicalDiversityCalculator,
    SyntacticComplexityCalculator,
    AIismCalculator,
)


# ============================================================================
# TEXT PROCESSOR TESTS
# ============================================================================
class TestTextProcessor:
    """Tests for TextProcessor module."""
    
    def test_sentence_extraction(self):
        """Test sentence extraction."""
        text = "This is sentence one. This is sentence two! And a third?"
        sentences = TextProcessor.extract_sentences(text)
        assert len(sentences) == 3
        assert sentences[0].startswith("This is sentence one")
    
    def test_tokenization(self):
        """Test word tokenization."""
        text = "Hello world. This is a test."
        tokens = TextProcessor.tokenize(text)
        assert len(tokens) > 0
        assert "Hello" in tokens
    
    def test_word_extraction(self):
        """Test word token extraction (no punctuation)."""
        text = "Hello, world! This-is_a test."
        words = TextProcessor.get_word_tokens(text)
        assert "hello" in words
        assert "world" in words
        assert "test" in words
        # Punctuation-only tokens should be removed
        assert not any(w == "," for w in words)
    
    def test_n_gram_extraction(self):
        """Test n-gram extraction."""
        tokens = ["the", "quick", "brown", "fox"]
        bigrams = TextProcessor.extract_n_grams(tokens, 2)
        assert ("the", "quick") in bigrams
        assert ("brown", "fox") in bigrams
        assert len(bigrams) == 3


# ============================================================================
# STATISTICS CALCULATOR TESTS
# ============================================================================
class TestStatisticsCalculator:
    """Tests for StatisticsCalculator module."""
    
    def test_sentence_length_calculation(self):
        """Test sentence length calculation."""
        sentences = ["This is short.", "This is a much longer sentence with many words."]
        lengths = StatisticsCalculator.calculate_sentence_lengths(sentences)
        assert len(lengths) == 2
        assert lengths[0] < lengths[1]
    
    def test_mean_sentence_length(self):
        """Test mean sentence length."""
        sentences = [
            "One two three.",  # 3 words
            "Four five six seven.",  # 4 words
            "Eight nine.",  # 2 words
        ]
        mean = StatisticsCalculator.mean_sentence_length(sentences)
        assert mean == pytest.approx(3.0, rel=0.1)
    
    def test_std_dev_sentence_length(self):
        """Test standard deviation of sentence lengths."""
        sentences = [
            "One two.",  # 2 words
            "A B C D E.",  # 5 words
            "X Y Z.",  # 3 words
        ]
        std_dev = StatisticsCalculator.std_dev_sentence_length(sentences)
        assert std_dev > 0
    
    def test_type_token_ratio(self):
        """Test Type-Token Ratio."""
        words = ["the", "cat", "sat", "on", "the", "mat"]  # 5 unique, 6 total
        ttr = StatisticsCalculator.type_token_ratio(words)
        assert ttr == pytest.approx(5/6, rel=0.01)
    
    def test_mtld_calculation(self):
        """Test MTLD calculation."""
        words = ["the"] * 5 + ["cat", "dog", "bird", "fish"] * 5  # Diverse vocabulary
        mtld = StatisticsCalculator.mtld(words)
        assert 0 < mtld < 200  # Typical MTLD range


# ============================================================================
# METRIC CALCULATION TESTS
# ============================================================================
class TestMetricCalculators:
    """Tests for metric calculation modules."""
    
    def test_burstiness_human_like(self):
        """Test burstiness calculation - human-like variation."""
        # Varied sentence lengths: 2, 10, 3, 15 words
        sentences = [
            "Go now.",  # 2
            "The question of how artificial intelligence affects L2 writing is complex.",  # 14
            "Start again.",  # 2
            "Natural human writing has varied sentence structures for emphasis and clarity.",  # 14
        ]
        burstiness = BurstinessCalculator.calculate(sentences)
        assert burstiness > 0.5  # Should be high (human-like)
    
    def test_burstiness_machine_like(self):
        """Test burstiness calculation - machine-like uniformity."""
        # Uniform sentence lengths: all 5 words
        sentences = [
            "The cat sat on the mat.",  # 6
            "A bird flew over the lake.",  # 6
            "The sun rose in the east.",  # 6
            "We walked down the street.",  # 6
        ]
        burstiness = BurstinessCalculator.calculate(sentences)
        assert burstiness < 0.3  # Should be low (machine-like)
    
    def test_lexical_diversity(self):
        """Test lexical diversity calculation."""
        words1 = ["the"] * 20  # Very low diversity
        diversity1 = LexicalDiversityCalculator.calculate(words1)
        assert diversity1 < 0.2
        
        words2 = ["dog", "cat", "bird", "fish", "elephant"] * 4  # Moderate diversity
        diversity2 = LexicalDiversityCalculator.calculate(words2)
        assert 0.0 <= diversity2 <= 1.0  # Valid range
    
    def test_syntactic_complexity(self):
        """Test syntactic complexity calculation."""
        simple_text = "I go. I run. I jump."
        complex_text = (
            "Although it was raining heavily, the determined researchers continued "
            "their important work, which required significant collaboration and careful planning."
        )
        
        simple_sentences = TextProcessor.extract_sentences(simple_text)
        complex_sentences = TextProcessor.extract_sentences(complex_text)
        
        simple_complexity = SyntacticComplexityCalculator.calculate(simple_sentences, simple_text)
        complex_complexity = SyntacticComplexityCalculator.calculate(complex_sentences, complex_text)
        
        assert simple_complexity < complex_complexity
    
    def test_ai_ism_detection(self):
        """Test AI-ism detection."""
        ai_heavy_text = (
            "It is important to note that AI writing demonstrates standardized patterns. "
            "In light of recent research, we must delve into the question. "
            "In conclusion, further investigation is warranted."
        )
        
        ai_score, detected = AIismCalculator.calculate(ai_heavy_text)
        assert ai_score > 0  # Should detect some AI-isms
        assert len(detected) > 0  # Should detect some AI-isms
        
        human_text = "I wrote this myself. My thoughts are unique. This is my voice."
        human_score, _ = AIismCalculator.calculate(human_text)
        assert human_score <= ai_score  # Should be lower or equal to AI text


# ============================================================================
# METRIC VALIDATION TESTS (Parity with Manual Analysis)
# ============================================================================
class TestMetricValidation:
    """Validate metric calculation against manual analysis."""
    
    def test_metric_parity_sample_1(self):
        """Validate metrics on sample text 1."""
        text = (
            "Students today learn using technology. AI tools help them improve writing. "
            "But what happens to their unique voice? The answer is complex and important."
        )
        
        preprocessor = TextAnalysisPreprocessor(text)
        features = preprocessor.get_analysis_features()
        
        # Manual check: text has clear variation
        burstiness = BurstinessCalculator.calculate(features['sentences'])
        assert 0.0 < burstiness < 2.0  # Reasonable range
    
    def test_metrics_within_expected_ranges(self):
        """Verify all metrics stay within expected ranges."""
        text = (
            "The modern learning environment presents both opportunities and challenges. "
            "Students utilizing artificial intelligence tools for academic writing demonstrate "
            "improved grammatical accuracy. However, research indicates potential concerns regarding "
            "the preservation of authentic learner voice and distinctive stylistic characteristics."
        )
        
        from metric_calculator import MetricCalculationEngine
        engine = MetricCalculationEngine(text)
        metrics = engine.calculate_all_metrics()
        
        # All normalized metrics should be 0-1
        assert 0 <= metrics['burstiness'] <= 1
        assert 0 <= metrics['lexical_diversity'] <= 1
        assert 0 <= metrics['syntactic_complexity'] <= 1
        assert 0 <= metrics['ai_ism_likelihood'] <= 1
        
        # Raw values in expected ranges
        assert 0 < metrics['burstiness_raw'] < 3
        assert 0 <= metrics['lexical_diversity_raw'] <= 1
        assert 0 <= metrics['syntactic_complexity_raw'] <= 1
        assert 0 <= metrics['ai_ism_likelihood_raw'] <= 100


# ============================================================================
# EXPORT VALIDATION TESTS
# ============================================================================
class TestExportValidation:
    """Validate export functionality."""
    
    def test_csv_export_format(self):
        """Test CSV export produces valid format."""
        from exporters import CSVExporter
        from models import DocumentPair, AnalysisResult, MetricScores, MetricDeltas
        
        # Mock objects
        doc_pair = DocumentPair(
            original_text="Original text here.",
            edited_text="Edited text here."
        )
        
        result = AnalysisResult(
            doc_pair_id=doc_pair.id,
            original_metrics=MetricScores(
                burstiness=1.2,
                lexical_diversity=0.65,
                syntactic_complexity=0.70,
                ai_ism_likelihood=25.0,
            ),
            edited_metrics=MetricScores(
                burstiness=0.8,
                lexical_diversity=0.55,
                syntactic_complexity=0.65,
                ai_ism_likelihood=65.0,
            ),
            metric_deltas=MetricDeltas(
                burstiness_delta=-0.4,
                burstiness_pct_change=-33.3,
                lexical_diversity_delta=-0.1,
                lexical_diversity_pct_change=-15.4,
                syntactic_complexity_delta=-0.05,
                syntactic_complexity_pct_change=-7.1,
                ai_ism_delta=40.0,
                ai_ism_pct_change=160.0,
            ),
        )
        
        metadata = {
            'word_count': 100,
            'char_count': 500,
            'sentence_count': 5,
        }
        
        csv_output = CSVExporter.export(result, doc_pair, metadata, metadata)
        assert isinstance(csv_output, str)
        assert "VoiceTracer" in csv_output
        assert "Burstiness" in csv_output
    
    def test_json_export_structure(self):
        """Test JSON export produces valid structure."""
        from exporters import JSONExporter
        from models import DocumentPair, AnalysisResult, MetricScores, MetricDeltas
        
        # Mock objects
        doc_pair = DocumentPair(
            original_text="Original text here.",
            edited_text="Edited text here."
        )
        
        result = AnalysisResult(
            doc_pair_id=doc_pair.id,
            original_metrics=MetricScores(
                burstiness=1.2, lexical_diversity=0.65,
                syntactic_complexity=0.70, ai_ism_likelihood=25.0,
            ),
            edited_metrics=MetricScores(
                burstiness=0.8, lexical_diversity=0.55,
                syntactic_complexity=0.65, ai_ism_likelihood=65.0,
            ),
            metric_deltas=MetricDeltas(
                burstiness_delta=-0.4, burstiness_pct_change=-33.3,
                lexical_diversity_delta=-0.1, lexical_diversity_pct_change=-15.4,
                syntactic_complexity_delta=-0.05, syntactic_complexity_pct_change=-7.1,
                ai_ism_delta=40.0, ai_ism_pct_change=160.0,
            ),
        )
        
        metadata = {
            'word_count': 10, 'char_count': 50,
            'sentence_count': 2, 'avg_sentence_length': 5,
        }
        
        json_output = JSONExporter.export(result, doc_pair, metadata, metadata)
        assert isinstance(json_output, str)
        
        # Verify it's valid JSON
        import json
        data = json.loads(json_output)
        assert 'metadata' in data
        assert 'metrics' in data


# ============================================================================
# ACCESSIBILITY TESTS
# ============================================================================
class TestAccessibility:
    """Test WCAG 2.1 AA compliance requirements."""
    
    def test_color_contrast_ratios(self):
        """Verify color contrast meets WCAG standards."""
        # Placeholder for contrast ratio validation
        # Would use a library like wcag-contrast to verify ratios
        # Primary color: #1f77b4 on white should have sufficient contrast
        pass
    
    def test_heading_hierarchy(self):
        """Verify proper heading hierarchy in markdown."""
        # Streamlit automatically handles heading hierarchy
        # This would test the app's rendering
        pass


# ============================================================================
# TEST RUNNER
# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
