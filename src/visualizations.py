"""
VoiceTracer Visualization Module

Generates interactive charts and visualizations for the dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import pandas as pd


class RadarChartGenerator:
    """Generates radar charts comparing original vs edited metrics."""
    
    @staticmethod
    def create_metric_radar(
        original_metrics: Dict[str, float],
        edited_metrics: Dict[str, float]
    ) -> go.Figure:
        """
        Create an 8-axis radar chart comparing original and edited texts.
        
        Axes:
        1. Burstiness (sentence variation)
        2. Lexical Diversity (vocabulary richness)
        3. Syntactic Complexity (structure sophistication)
        4. AI-ism Likelihood (human-like)
        5. Function Word Ratio (human-like)
        6. Discourse Marker Density (human-like)
        7. Information Density (human-like)
        8. Epistemic Hedging (human-like)
        
        Args:
            original_metrics: Metrics dict from original text
            edited_metrics: Metrics dict from edited text
        
        Returns:
            Plotly figure object
        """
        
        # Prepare data
        categories = [
            'Burstiness<br>(Variation)',
            'Lexical Diversity<br>(Vocabulary)',
            'Syntactic Complexity<br>(Structure)',
            'AI-ism<br>(Human-like)',
            'Function Words<br>(Human-like)',
            'Discourse Markers<br>(Human-like)',
            'Information Density<br>(Human-like)',
            'Hedging<br>(Human-like)'
        ]

        def to_human_like(values: Dict[str, float]) -> List[float]:
            """Convert normalized metrics to a consistent human-like direction."""
            return [
                values.get('burstiness', 0),
                values.get('lexical_diversity', 0),
                values.get('syntactic_complexity', 0),
                values.get('ai_ism_likelihood', 0),
                1 - values.get('function_word_ratio', 0),
                1 - values.get('discourse_marker_density', 0),
                1 - values.get('information_density', 0),
                1 - values.get('epistemic_hedging', 0),
            ]
        
        # Original values (already normalized 0-1)
        original_values = to_human_like(original_metrics)
        
        # Edited values
        edited_values = to_human_like(edited_metrics)
        
        fig = go.Figure()
        
        # Add original trace
        fig.add_trace(go.Scatterpolar(
            r=original_values,
            theta=categories,
            fill='toself',
            name='Original',
            line=dict(color='#2ca02c', width=2),
            fillcolor='rgba(44, 160, 44, 0.3)',
        ))
        
        # Add edited trace
        fig.add_trace(go.Scatterpolar(
            r=edited_values,
            theta=categories,
            fill='toself',
            name='Edited',
            line=dict(color='#d62728', width=2),
            fillcolor='rgba(214, 39, 40, 0.3)',
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                )
            ),
            showlegend=True,
            title="Core 8 Metric Comparison: Original vs Edited",
            height=600,
            hovermode='closest',
        )
        
        return fig


class BarChartGenerator:
    """Generates bar charts for metric comparison."""
    
    @staticmethod
    def create_metric_comparison(
        original_metrics: Dict[str, float],
        edited_metrics: Dict[str, float]
    ) -> go.Figure:
        """
        Create a side-by-side bar chart for metric comparison.
        
        Args:
            original_metrics: Metrics dict from original text
            edited_metrics: Metrics dict from edited text
        
        Returns:
            Plotly figure object
        """
        
        metrics = [
            ('Burstiness', original_metrics.get('burstiness_raw', 0), edited_metrics.get('burstiness_raw', 0), 3.0),
            ('Lexical Diversity', original_metrics.get('lexical_diversity_raw', 0), edited_metrics.get('lexical_diversity_raw', 0), 1.0),
            ('Syntactic Complexity', original_metrics.get('syntactic_complexity_raw', 0), edited_metrics.get('syntactic_complexity_raw', 0), 1.0),
            ('AI-ism Likelihood', original_metrics.get('ai_ism_likelihood_raw', 0), edited_metrics.get('ai_ism_likelihood_raw', 0), 100),
            ('Function Word Ratio', original_metrics.get('function_word_ratio_raw', 0), edited_metrics.get('function_word_ratio_raw', 0), 1.0),
            ('Discourse Marker Density', original_metrics.get('discourse_marker_density_raw', 0), edited_metrics.get('discourse_marker_density_raw', 0), 30.0),
            ('Information Density', original_metrics.get('information_density_raw', 0), edited_metrics.get('information_density_raw', 0), 1.0),
            ('Epistemic Hedging', original_metrics.get('epistemic_hedging_raw', 0), edited_metrics.get('epistemic_hedging_raw', 0), 0.15),
        ]
        
        names = [m[0] for m in metrics]
        original_vals = [m[1] for m in metrics]
        edited_vals = [m[2] for m in metrics]
        
        fig = go.Figure(data=[
            go.Bar(name='Original', x=names, y=original_vals, marker_color='#2ca02c'),
            go.Bar(name='Edited', x=names, y=edited_vals, marker_color='#d62728')
        ])
        
        fig.update_layout(
            barmode='group',
            title='Metric Values: Original vs Edited',
            xaxis_title='Metric',
            yaxis_title='Value',
            height=400,
            hovermode='x unified',
        )
        
        return fig


class IndividualMetricCharts:
    """Generates individual metric comparison charts."""

    @staticmethod
    def create_metric_panels(
        original_metrics: Dict[str, float],
        edited_metrics: Dict[str, float]
    ) -> List[Tuple[str, go.Figure]]:
        """Create one chart per metric for side-by-side comparison."""
        metrics = [
            ('Burstiness', 'burstiness_raw', 3.0),
            ('Lexical Diversity', 'lexical_diversity_raw', 1.0),
            ('Syntactic Complexity', 'syntactic_complexity_raw', 1.0),
            ('AI-ism Likelihood', 'ai_ism_likelihood_raw', 100.0),
            ('Function Word Ratio', 'function_word_ratio_raw', 1.0),
            ('Discourse Marker Density', 'discourse_marker_density_raw', 30.0),
            ('Information Density', 'information_density_raw', 1.0),
            ('Epistemic Hedging', 'epistemic_hedging_raw', 0.15),
        ]

        panels = []
        for name, key, max_val in metrics:
            orig_val = original_metrics.get(key, 0)
            edit_val = edited_metrics.get(key, 0)

            fig = go.Figure(data=[
                go.Bar(
                    name='Original',
                    x=['Original'],
                    y=[orig_val],
                    marker_color='#2ca02c',
                ),
                go.Bar(
                    name='Edited',
                    x=['Edited'],
                    y=[edit_val],
                    marker_color='#d62728',
                )
            ])

            fig.update_layout(
                title=name,
                barmode='group',
                height=260,
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False,
                yaxis=dict(range=[0, max_val], title='Value'),
            )

            panels.append((name, fig))

        return panels


class DeltaVisualization:
    """Generates visualizations of metric changes."""
    
    @staticmethod
    def create_delta_chart(deltas: Dict[str, float]) -> go.Figure:
        """
        Create a waterfall or bar chart showing metric changes.
        
        Args:
            deltas: Delta dict from MetricComparisonEngine
        
        Returns:
            Plotly figure object
        """
        
        metric_names = [
            'Burstiness',
            'Lexical Diversity',
            'Syntactic Complexity',
            'AI-ism Likelihood',
            'Function Word Ratio',
            'Discourse Marker Density',
            'Information Density',
            'Epistemic Hedging',
        ]
        changes_pct = [
            deltas.get('burstiness_pct_change', 0),
            deltas.get('lexical_diversity_pct_change', 0),
            deltas.get('syntactic_complexity_pct_change', 0),
            deltas.get('ai_ism_likelihood_pct_change', 0),
            deltas.get('function_word_ratio_pct_change', 0),
            deltas.get('discourse_marker_density_pct_change', 0),
            deltas.get('information_density_pct_change', 0),
            deltas.get('epistemic_hedging_pct_change', 0),
        ]
        
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in changes_pct]
        
        fig = go.Figure(data=[
            go.Bar(
                x=metric_names,
                y=changes_pct,
                marker_color=colors,
                text=[f'{x:+.3f}' for x in changes_pct],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Metric Shifts (Original → Edited)',
            xaxis_title='Metric',
            yaxis_title='Absolute Shift (Δ)',
            height=400,
            hovermode='x unified',
            shapes=[
                dict(
                    type='line',
                    x0=-0.5,
                    y0=0,
                    x1=len(metric_names)-0.5,
                    y1=0,
                    line=dict(color='gray', width=1, dash='dash'),
                )
            ]
        )
        
        return fig


class TextDiffVisualizer:
    """Generates side-by-side text diffs."""
    
    @staticmethod
    def create_text_diff_html(original_text: str, edited_text: str) -> str:
        """
        Create HTML visualization of text differences.
        
        Args:
            original_text: Original text
            edited_text: Edited text
        
        Returns:
            HTML string for rendering
        """
        # Simple diff: highlight added/removed words
        orig_words = original_text.split()
        edit_words = edited_text.split()
        
        # This is a simplified version; full implementation would use difflib
        html = """
        <style>
            .diff-container { display: flex; gap: 20px; margin: 20px 0; }
            .diff-side { flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .diff-added { background-color: #d4edda; }
            .diff-removed { background-color: #f8d7da; }
            .diff-neutral { color: #333; }
        </style>
        <div class="diff-container">
            <div class="diff-side">
                <h4>Original</h4>
                <p>
        """
        
        for word in orig_words[:50]:  # Limit display
            html += f'<span class="diff-neutral">{word}</span> '
        
        html += """
                </p>
            </div>
            <div class="diff-side">
                <h4>Edited</h4>
                <p>
        """
        
        for word in edit_words[:50]:
            html += f'<span class="diff-neutral">{word}</span> '
        
        html += """
                </p>
            </div>
        </div>
        """
        
        return html


class MetricsOverTimeChart:
    """Generates time-series visualizations for multiple analyses."""
    
    @staticmethod
    def create_timeline(analysis_history: List[Dict]) -> go.Figure:
        """
        Create a time-series chart if user analyzes multiple versions.
        
        Args:
            analysis_history: List of analysis results over time
        
        Returns:
            Plotly figure object
        """
        # Create dataframe from history
        df = pd.DataFrame([
            {
                'timestamp': a.get('timestamp', ''),
                'burstiness': a.get('metrics', {}).get('burstiness', 0),
                'lex_div': a.get('metrics', {}).get('lexical_diversity', 0),
                'syn_complex': a.get('metrics', {}).get('syntactic_complexity', 0),
            }
            for a in analysis_history
        ])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['burstiness'],
            mode='lines+markers',
            name='Burstiness',
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['lex_div'],
            mode='lines+markers',
            name='Lexical Diversity',
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['syn_complex'],
            mode='lines+markers',
            name='Syntactic Complexity',
        ))
        
        fig.update_layout(
            title='Metrics Over Time (Multiple Analyses)',
            xaxis_title='Analysis',
            yaxis_title='Metric Value',
            height=400,
            hovermode='x unified',
        )
        
        return fig


class BurstinessVisualization:
    """Generates detailed burstiness analysis charts."""
    
    @staticmethod
    def create_sentence_length_bars(original_text: str, edited_text: str) -> Tuple[go.Figure, Dict]:
        """
        Create bar chart showing word count per sentence for both texts.
        
        Args:
            original_text: Original text
            edited_text: Edited text
        
        Returns:
            Tuple of (Plotly figure object, statistics dict)
        """
        # Split texts into sentences
        import re
        
        def split_sentences(text: str) -> List[str]:
            """Split text into sentences."""
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
        
        def get_word_counts(sentences: List[str]) -> List[int]:
            """Get word count for each sentence."""
            return [len(s.split()) for s in sentences]
        
        original_sentences = split_sentences(original_text)
        edited_sentences = split_sentences(edited_text)
        
        original_counts = get_word_counts(original_sentences)
        edited_counts = get_word_counts(edited_sentences)
        
        # Calculate statistics
        import numpy as np
        
        orig_avg = float(np.mean(original_counts)) if original_counts else 0.0
        orig_var = float(np.var(original_counts)) if original_counts else 0.0
        edit_avg = float(np.mean(edited_counts)) if edited_counts else 0.0
        edit_var = float(np.var(edited_counts)) if edited_counts else 0.0
        
        # Determine pattern
        def classify_pattern(variance: float) -> str:
            if variance < 2.0:
                return "Machine-like Pattern"
            elif variance < 4.0:
                return "Moderate Pattern"
            else:
                return "Human-like Pattern"
        
        stats = {
            'original': {
                'avg_words': orig_avg,
                'variance': orig_var,
                'pattern': classify_pattern(orig_var)
            },
            'edited': {
                'avg_words': edit_avg,
                'variance': edit_var,
                'pattern': classify_pattern(edit_var)
            }
        }
        
        # Create visualization - show first 10 sentences for clarity
        max_sentences = min(10, max(len(original_counts), len(edited_counts)))
        sentence_indices = list(range(1, max_sentences + 1))
        
        original_display = original_counts[:max_sentences] + [0] * (max_sentences - len(original_counts[:max_sentences]))
        edited_display = edited_counts[:max_sentences] + [0] * (max_sentences - len(edited_counts[:max_sentences]))
        
        fig = go.Figure()
        
        # Add original trace (green for human)
        fig.add_trace(go.Bar(
            x=sentence_indices,
            y=original_display,
            name='Original (Human)',
            marker_color='#2ca02c',
            opacity=0.8,
        ))
        
        # Add edited trace (red for AI)
        fig.add_trace(go.Bar(
            x=sentence_indices,
            y=edited_display,
            name='Edited (AI)',
            marker_color='#d62728',
            opacity=0.8,
        ))
        
        fig.update_layout(
            title='Word Count per Sentence',
            xaxis_title='Sentence Index',
            yaxis_title='Word Count (WC)',
            barmode='group',
            height=350,
            hovermode='x unified',
            showlegend=True,
        )
        
        return fig, stats
    
    @staticmethod
    def create_fluctuation_curve(original_text: str, edited_text: str) -> go.Figure:
        """
        Create line chart showing fluctuation pattern across sentences.
        
        Args:
            original_text: Original text
            edited_text: Edited text
        
        Returns:
            Plotly figure object
        """
        import re
        
        def split_sentences(text: str) -> List[str]:
            """Split text into sentences."""
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
        
        def get_word_counts(sentences: List[str]) -> List[int]:
            """Get word count for each sentence."""
            return [len(s.split()) for s in sentences]
        
        original_sentences = split_sentences(original_text)
        edited_sentences = split_sentences(edited_text)
        
        original_counts = get_word_counts(original_sentences)
        edited_counts = get_word_counts(edited_sentences)
        
        # Show first 10 sentences for clarity
        max_sentences = min(10, max(len(original_counts), len(edited_counts)))
        sentence_indices = list(range(1, max_sentences + 1))
        
        original_display = original_counts[:max_sentences]
        edited_display = edited_counts[:max_sentences]
        
        fig = go.Figure()
        
        # Add original trace (green for human)
        fig.add_trace(go.Scatter(
            x=sentence_indices,
            y=original_display,
            mode='lines+markers',
            name='Original (Human)',
            line=dict(color='#2ca02c', width=3),
            marker=dict(size=8),
        ))
        
        # Add edited trace (red for AI)
        fig.add_trace(go.Scatter(
            x=sentence_indices,
            y=edited_display,
            mode='lines+markers',
            name='Edited (AI)',
            line=dict(color='#d62728', width=3),
            marker=dict(size=8),
        ))
        
        fig.update_layout(
            title='Fluctuation Pattern',
            xaxis_title='Sentence Index',
            yaxis_title='Word Count',
            height=300,
            hovermode='x unified',
            showlegend=True,
        )
        
        return fig
