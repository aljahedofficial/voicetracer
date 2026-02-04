"""
VoiceTracer Metric Calculation Engine

Calculates all metrics (burstiness, lexical diversity, syntactic complexity, AI-isms).
"""

from typing import Dict, List, Tuple
import re
from text_processor import (
    TextAnalysisPreprocessor,
    StatisticsCalculator,
    TextProcessor,
)
from metrics_spec import (
    AI_ISM_PHRASES,
    MetricType,
    normalize_metric,
)


class BurstinessCalculator:
    """Calculates burstiness (sentence length variation)."""
    
    @staticmethod
    def calculate(sentences: List[str]) -> float:
        """
        Calculate burstiness index.
        
        Formula: std_dev(sentence_lengths) / mean(sentence_lengths)
        
        Returns:
            Burstiness value (typically 0.5-2.5)
        """
        if not sentences or len(sentences) < 2:
            return 0.0
        
        mean_len = StatisticsCalculator.mean_sentence_length(sentences)
        std_dev = StatisticsCalculator.std_dev_sentence_length(sentences)
        
        if mean_len == 0:
            return 0.0
        
        burstiness = std_dev / mean_len
        return round(burstiness, 3)


class LexicalDiversityCalculator:
    """Calculates lexical diversity."""
    
    @staticmethod
    def calculate(words: List[str]) -> float:
        """
        Calculate lexical diversity using MTLD.
        
        Returns:
            Normalized diversity score 0-1
            (based on MTLD, scaled and normalized)
        """
        if not words:
            return 0.0
        
        mtld = StatisticsCalculator.mtld(words)
        
        # Normalize MTLD to 0-1 scale
        # MTLD typically ranges 70-150 for diverse texts
        # Scale: (MTLD - 70) / 110, capped at 1.0
        normalized = (mtld - 70.0) / 110.0
        normalized = max(0.0, min(normalized, 1.0))
        
        return round(normalized, 3)


class SyntacticComplexityCalculator:
    """Calculates syntactic complexity (composite metric)."""
    
    @staticmethod
    def calculate(sentences: List[str], text: str) -> float:
        """
        Calculate syntactic complexity.
        
        Composite of:
        - Average Sentence Length (ASL) - 40% weight
        - Subordination Ratio - 30% weight
        - Modifier Density - 30% weight
        
        Returns:
            Complexity score 0-1
        """
        if not sentences:
            return 0.0
        
        # 1. ASL component (0-1)
        asl = StatisticsCalculator.mean_sentence_length(sentences)
        # Normalize: assume typical range 10-30 words
        asl_norm = min(asl / 30.0, 1.0)
        
        # 2. Subordination component (0-1)
        subordination_scores = [
            StatisticsCalculator.subordination_ratio(s) for s in sentences
        ]
        avg_subordination = (
            sum(subordination_scores) / len(subordination_scores)
            if subordination_scores else 0.0
        )
        
        # 3. Modifier density component (0-1)
        mod_density = StatisticsCalculator.modifier_density(text)
        
        # Composite score
        complexity = (asl_norm * 0.4) + (avg_subordination * 0.3) + (mod_density * 0.3)
        
        return round(min(complexity, 1.0), 3)


class AIismCalculator:
    """Calculates AI-ism likelihood."""
    
    @staticmethod
    def calculate(text: str) -> Tuple[float, List[Dict]]:
        """
        Calculate AI-ism likelihood score and detect individual AI-isms.
        
        Returns:
            Tuple of (overall_score 0-100, list of detected AI-isms with details)
        """
        if not text:
            return 0.0, []
        
        text_lower = text.lower()
        detected_isms = []
        scores_by_category = {}
        
        # Check each category
        for category, phrases in AI_ISM_PHRASES.items():
            category_score = 0.0
            occurrences = []
            
            for phrase in phrases:
                # Find all occurrences of this phrase
                pattern = r'\b' + re.escape(phrase) + r'\b'
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                
                if matches:
                    count = len(matches)
                    occurrences.append({
                        'phrase': phrase,
                        'count': count,
                    })
                    # Add to detected list
                    for match in matches[:2]:  # Show up to 2 examples per phrase
                        # Extract context (50 chars before and after)
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end].strip()
                        
                        detected_isms.append({
                            'phrase': phrase,
                            'category': category,
                            'context': context,
                        })
            
            # Calculate category score (points based on frequency)
            if occurrences:
                total_count = sum(o['count'] for o in occurrences)
                # 0-3 occurrences: minimal score
                # 3-6: moderate score
                # 6+: high score
                if total_count <= 3:
                    category_score = min(total_count * 3, 30)  # 0-30 max per category
                elif total_count <= 6:
                    category_score = 20 + (total_count - 3) * 3
                else:
                    category_score = 30
            
            scores_by_category[category] = min(category_score, 30)
        
        # Passive voice bonus
        passive_ratio = TextProcessor.get_passive_voice_ratio(text)
        passive_score = passive_ratio * 20 if passive_ratio > 0.25 else 0
        
        # Sum category scores (max 30 each for 4 categories = 120)
        # Normalize to 0-100
        total_score = sum(scores_by_category.values()) + passive_score
        normalized_score = min((total_score / 120.0) * 100, 100)
        
        return round(normalized_score, 1), detected_isms


class MetricCalculationEngine:
    """Main engine for calculating all metrics."""
    
    def __init__(self, text: str):
        self.text = text
        self.preprocessor = TextAnalysisPreprocessor(text)
        self.features = self.preprocessor.get_analysis_features()
    
    def calculate_all_metrics(self) -> Dict[str, float]:
        """
        Calculate all metrics for the text.
        
        Returns:
            Dict with metric names as keys and values 0-1 (normalized)
        """
        metrics = {}
        
        # Burstiness
        burstiness = BurstinessCalculator.calculate(self.features['sentences'])
        metrics['burstiness'] = normalize_metric(burstiness, MetricType.BURSTINESS)
        metrics['burstiness_raw'] = burstiness
        
        # Lexical Diversity
        lex_div = LexicalDiversityCalculator.calculate(self.features['words'])
        metrics['lexical_diversity'] = lex_div
        metrics['lexical_diversity_raw'] = lex_div
        
        # Syntactic Complexity
        syn_complex = SyntacticComplexityCalculator.calculate(
            self.features['sentences'],
            self.text
        )
        metrics['syntactic_complexity'] = syn_complex
        metrics['syntactic_complexity_raw'] = syn_complex
        
        # AI-ism Likelihood
        ai_ism_score, detected = AIismCalculator.calculate(self.text)
        metrics['ai_ism_likelihood'] = normalize_metric(ai_ism_score, MetricType.AI_ISM_LIKELIHOOD)
        metrics['ai_ism_likelihood_raw'] = ai_ism_score
        metrics['ai_isms_detected'] = detected
        
        return metrics
    
    def get_metadata(self) -> Dict:
        """Get text metadata."""
        return self.preprocessor.get_metadata()


class MetricComparisonEngine:
    """Compares metrics between original and edited texts."""
    
    @staticmethod
    def calculate_deltas(
        original_metrics: Dict[str, float],
        edited_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate metric changes (deltas).
        
        Args:
            original_metrics: Metrics from original text
            edited_metrics: Metrics from edited text
        
        Returns:
            Dict with delta values and percent changes
        """
        deltas = {}
        range_max_by_metric = {
            'burstiness': 3.0,
            'lexical_diversity': 1.0,
            'syntactic_complexity': 1.0,
            'ai_ism_likelihood': 100.0,
        }
        
        for key in ['burstiness', 'lexical_diversity', 'syntactic_complexity', 'ai_ism_likelihood']:
            raw_key = key + '_raw'
            
            orig_val = original_metrics.get(raw_key, 0.0)
            edit_val = edited_metrics.get(raw_key, 0.0)
            
            delta = edit_val - orig_val
            scale_max = range_max_by_metric.get(key, 1.0)
            pct_change = (delta / scale_max * 100) if scale_max else 0.0
            
            deltas[f'{key}_delta'] = round(delta, 3)
            deltas[f'{key}_pct_change'] = round(pct_change, 1)
        
        return deltas
    
    @staticmethod
    def generate_change_narratives(deltas: Dict[str, float]) -> Dict[str, str]:
        """
        Generate human-readable narratives for metric changes.
        
        Args:
            deltas: Delta dict from calculate_deltas
        
        Returns:
            Dict with narrative explanations for each metric change
        """
        narratives = {}
        
        # Burstiness narrative
        burst_delta = deltas.get('burstiness_delta', 0)
        burst_pct = deltas.get('burstiness_pct_change', 0)
        if burst_delta < -0.3:
            narratives['burstiness'] = (
                f"Sentence length variation decreased by {abs(burst_pct):.0f}%. "
                "AI editing standardized your sentence lengths for clarity and consistency."
            )
        elif burst_delta > 0.2:
            narratives['burstiness'] = (
                f"Sentence variation increased by {burst_pct:.0f}%. "
                "This suggests more natural, diverse sentence structures."
            )
        else:
            narratives['burstiness'] = "Minimal change in sentence length variation."
        
        # Lexical diversity narrative
        lex_delta = deltas.get('lexical_diversity_delta', 0)
        lex_pct = deltas.get('lexical_diversity_pct_change', 0)
        if lex_delta < -0.15:
            narratives['lexical_diversity'] = (
                f"Vocabulary diversity decreased by {abs(lex_pct):.0f}%. "
                "AI editing replaced varied vocabulary with common academic phrases."
            )
        elif lex_delta > 0.1:
            narratives['lexical_diversity'] = (
                f"Vocabulary diversity increased by {lex_pct:.0f}%. "
                "This is rare but suggests the editor maintained or expanded vocabulary."
            )
        else:
            narratives['lexical_diversity'] = "Minimal change in vocabulary diversity."
        
        # Syntactic complexity narrative
        syn_delta = deltas.get('syntactic_complexity_delta', 0)
        syn_pct = deltas.get('syntactic_complexity_pct_change', 0)
        if syn_delta < -0.1:
            narratives['syntactic_complexity'] = (
                f"Syntactic complexity decreased by {abs(syn_pct):.0f}%. "
                "AI editing simplified sentence structures, possibly removing original complexity."
            )
        elif syn_delta > 0.1:
            narratives['syntactic_complexity'] = (
                f"Syntactic complexity increased by {syn_pct:.0f}%. "
                "The edited version uses more sophisticated structures."
            )
        else:
            narratives['syntactic_complexity'] = "Minimal change in syntactic complexity."
        
        # AI-ism narrative
        ai_delta = deltas.get('ai_ism_likelihood_delta', 0)
        ai_pct = deltas.get('ai_ism_likelihood_pct_change', 0)
        if ai_delta > 0.2:
            narratives['ai_ism_likelihood'] = (
                f"AI-ism markers increased by {ai_pct:.0f}%. "
                "The edited version contains significantly more AI-characteristic phrases and patterns."
            )
        elif ai_delta < -0.1:
            narratives['ai_ism_likelihood'] = (
                f"AI-ism markers decreased by {abs(ai_pct):.0f}%. "
                "The edits introduced some more natural, human-like language."
            )
        else:
            narratives['ai_ism_likelihood'] = "AI-ism markers remained largely unchanged."
        
        return narratives
