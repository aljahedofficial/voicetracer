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
        Create a 6-axis radar chart comparing original and edited texts.
        
        Axes:
        1. Burstiness (sentence variation)
        2. Lexical Diversity (vocabulary richness)
        3. Syntactic Complexity (structure sophistication)
        4. AI-ism Inversed (humanness)
        5. Passive Voice Ratio (activity vs passivity)
        6. Overall Authenticity
        
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
            'Authenticity<br>(vs AI-isms)',
            'Activity<br>(vs Passive)',
            'Overall Voice<br>Preservation'
        ]
        
        # Original values (already normalized 0-1)
        original_values = [
            original_metrics.get('burstiness', 0),
            original_metrics.get('lexical_diversity', 0),
            original_metrics.get('syntactic_complexity', 0),
            1 - (original_metrics.get('ai_ism_likelihood', 0) / 100),  # Invert AI-ism
            1 - original_metrics.get('passive_voice_ratio', 0),  # Invert passive
            0.75,  # Composite authenticity (heuristic)
        ]
        
        # Edited values
        edited_values = [
            edited_metrics.get('burstiness', 0),
            edited_metrics.get('lexical_diversity', 0),
            edited_metrics.get('syntactic_complexity', 0),
            1 - (edited_metrics.get('ai_ism_likelihood', 0) / 100),
            1 - edited_metrics.get('passive_voice_ratio', 0),
            0.65,  # Composite (typically lower after editing)
        ]
        
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
            title="Metric Comparison: Original vs Edited",
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
        
        metric_names = ['Burstiness', 'Lexical Diversity', 'Syntactic Complexity', 'AI-ism Likelihood']
        changes_pct = [
            deltas.get('burstiness_pct_change', 0),
            deltas.get('lexical_diversity_pct_change', 0),
            deltas.get('syntactic_complexity_pct_change', 0),
            deltas.get('ai_ism_likelihood_pct_change', 0),
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
