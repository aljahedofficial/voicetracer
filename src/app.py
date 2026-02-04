"""
VoiceTracer - Streamlit Web Application

Main entry point. Implements the 4-step dashboard workflow.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models import DocumentPair, AnalysisResult, MetricScores, MetricDeltas, Session
from metric_calculator import MetricCalculationEngine, MetricComparisonEngine, AIismCalculator
from text_processor import TextProcessor


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="VoiceTracer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main color scheme */
    :root {
        --primary: #1f77b4;
        --success: #2ca02c;
        --warning: #ff7f0e;
        --danger: #d62728;
        --light-bg: #f8f9fa;
    }
    
    /* Cards */
    .metric-card {
        padding: 20px;
        border-radius: 8px;
        background: white;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Headers */
    h1 { color: #1f1f1f; margin-bottom: 0.5em; }
    h2 { color: #333; margin: 0.8em 0 0.4em 0; }
    h3 { color: #555; }
    
    /* Accessibility */
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR NAVIGATION & SETUP
# ============================================================================
def setup_sidebar():
    """Setup sidebar navigation and settings."""
    with st.sidebar:
        st.markdown("## 🎙️ VoiceTracer")
        st.markdown("---")
        
        st.markdown("### About")
        st.info(
            "VoiceTracer measures stylistic changes when L2 writers use AI editing tools. "
            "Compare your original and edited texts to understand voice preservation."
        )
        
        st.markdown("### Navigation")
        current_step = st.radio(
            "Select Step:",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "📝 Step 1: Input",
                2: "📊 Step 2: Metrics",
                3: "📈 Step 3: Visualize",
                4: "📄 Step 4: Export"
            }[x],
            key="nav_step"
        )
        
        st.markdown("---")
        st.markdown("### Session")
        
        if 'doc_pair' in st.session_state:
            st.success(f"✓ Documents loaded")
            if 'analysis_result' in st.session_state:
                st.success(f"✓ Analysis complete")
        
        st.markdown("---")
        st.markdown("### Help")
        with st.expander("How to use"):
            st.markdown("""
            1. **Input** your original and edited texts
            2. **View** metrics comparing the two versions
            3. **Visualize** the differences with charts
            4. **Export** reports in multiple formats
            """)
        
        st.markdown("---")
        st.caption("Made for thesis research on stylistic homogenization in L2 writing")
        
        return current_step


# ============================================================================
# STEP 1: INPUT PANEL
# ============================================================================
def render_step_1_input():
    """Step 1: Accept text input from user."""
    st.title("📝 Step 1: Input Text")
    
    st.markdown("""
    Enter your **original** and **AI-edited** texts below. You can paste text, upload files, 
    or load sample texts.
    """)

    # Sample loader (must run before widget creation to avoid session_state conflicts)
    st.markdown("#### Load Sample Texts")
    if st.button("📌 Load Example", key="load_example"):
        st.session_state.original_input = (
            "The research about artificial intelligence and language learning show that "
            "students who use AI tools get better grades quickly. However, we must think about "
            "what happens to their own writing voice. When students rely too much on AI, "
            "their writing becomes more uniform. It is important that we study this phenomenon. "
            "The problem is complex because AI tools help students improve grammar, but at same time "
            "they may lose their unique style."
        )
        st.session_state.edited_input = (
            "Research examining the intersection of artificial intelligence and language acquisition "
            "demonstrates that students utilizing AI-assisted tools achieve improved academic performance metrics. "
            "However, it is important to note that significant considerations must be given to the preservation "
            "of authentic learner voice. Overreliance on artificial intelligence assistance can result in stylistic "
            "homogenization of written output. Therefore, it is evident that systematic investigation of this phenomenon "
            "is warranted. The complexity of this issue is noteworthy, as artificial intelligence tools facilitate "
            "grammatical improvement while simultaneously creating the potential for diminished stylistic individuality."
        )
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Text")
        original_text = st.text_area(
            label="Original (unassisted) writing",
            height=300,
            key="original_input",
            placeholder="Paste your original text here...",
        )
    
    with col2:
        st.subheader("Edited Text")
        edited_text = st.text_area(
            label="AI-edited version",
            height=300,
            key="edited_input",
            placeholder="Paste the AI-edited version here...",
        )
    
    # File upload section
    st.markdown("#### Upload Files (Optional)")
    col1_up, col2_up = st.columns(2)
    
    with col1_up:
        orig_file = st.file_uploader("Upload original text", key="orig_file", type=['txt'])
        if orig_file:
            original_text = orig_file.read().decode('utf-8')
    
    with col2_up:
        edit_file = st.file_uploader("Upload edited text", key="edit_file", type=['txt'])
        if edit_file:
            edited_text = edit_file.read().decode('utf-8')
    
    # Text statistics
    if original_text or edited_text:
        st.markdown("#### Quick Statistics")
        
        stat_col1, stat_col2 = st.columns(2)
        
        with stat_col1:
            orig_words = len(original_text.split()) if original_text else 0
            st.metric("Original: Words", orig_words)
        
        with stat_col2:
            edit_words = len(edited_text.split()) if edited_text else 0
            st.metric("Edited: Words", edit_words)
    
    # Proceed button
    st.markdown("---")
    
    if st.button("✓ Analyze Texts", key="analyze_btn", type="primary"):
        if not original_text.strip() or not edited_text.strip():
            st.error("Please enter or upload both original and edited texts.")
        else:
            # Create document pair and run analysis
            doc_pair = DocumentPair(
                original_text=original_text,
                edited_text=edited_text
            )
            st.session_state.doc_pair = doc_pair
            
            # Calculate metrics
            with st.spinner("Analyzing texts..."):
                orig_engine = MetricCalculationEngine(original_text)
                edit_engine = MetricCalculationEngine(edited_text)
                
                orig_metrics = orig_engine.calculate_all_metrics()
                edit_metrics = edit_engine.calculate_all_metrics()
                
                # Get AI-isms
                _, ai_isms = AIismCalculator.calculate(edited_text)
                
                # Create result
                metric_scores_orig = MetricScores(
                    burstiness=orig_metrics['burstiness_raw'],
                    lexical_diversity=orig_metrics['lexical_diversity_raw'],
                    syntactic_complexity=orig_metrics['syntactic_complexity_raw'],
                    ai_ism_likelihood=orig_metrics['ai_ism_likelihood_raw'],
                )
                
                metric_scores_edit = MetricScores(
                    burstiness=edit_metrics['burstiness_raw'],
                    lexical_diversity=edit_metrics['lexical_diversity_raw'],
                    syntactic_complexity=edit_metrics['syntactic_complexity_raw'],
                    ai_ism_likelihood=edit_metrics['ai_ism_likelihood_raw'],
                )
                
                deltas = MetricComparisonEngine.calculate_deltas(orig_metrics, edit_metrics)
                
                metric_deltas = MetricDeltas(
                    burstiness_delta=deltas['burstiness_delta'],
                    burstiness_pct_change=deltas['burstiness_pct_change'],
                    lexical_diversity_delta=deltas['lexical_diversity_delta'],
                    lexical_diversity_pct_change=deltas['lexical_diversity_pct_change'],
                    syntactic_complexity_delta=deltas['syntactic_complexity_delta'],
                    syntactic_complexity_pct_change=deltas['syntactic_complexity_pct_change'],
                    ai_ism_delta=deltas['ai_ism_likelihood_delta'],
                    ai_ism_pct_change=deltas['ai_ism_likelihood_pct_change'],
                )
                
                result = AnalysisResult(
                    doc_pair_id=doc_pair.id,
                    original_metrics=metric_scores_orig,
                    edited_metrics=metric_scores_edit,
                    metric_deltas=metric_deltas,
                    ai_isms=ai_isms[:10],  # Keep first 10 detected
                )
                
                st.session_state.analysis_result = result
                st.session_state.orig_engine = orig_engine
                st.session_state.edit_engine = edit_engine
            
            st.success("✓ Analysis complete! Go to Step 2 to view metrics.")


# ============================================================================
# STEP 2: METRICS DASHBOARD
# ============================================================================
def render_step_2_metrics():
    """Step 2: Display metrics and explanations."""
    st.title("📊 Step 2: Metrics Dashboard")
    
    if 'analysis_result' not in st.session_state:
        st.warning("⚠️ Please complete Step 1 first.")
        return
    
    result = st.session_state.analysis_result
    
    st.markdown("### Quick Summary")
    st.markdown("Compare your metrics across 4 key dimensions:")
    
    # Metric cards in grid
    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
    
    metrics_info = [
        ("Burstiness", result.original_metrics.burstiness, result.edited_metrics.burstiness, result.metric_deltas.burstiness_pct_change),
        ("Lexical Diversity", result.original_metrics.lexical_diversity, result.edited_metrics.lexical_diversity, result.metric_deltas.lexical_diversity_pct_change),
        ("Syntactic Complexity", result.original_metrics.syntactic_complexity, result.edited_metrics.syntactic_complexity, result.metric_deltas.syntactic_complexity_pct_change),
        ("AI-ism Likelihood", result.original_metrics.ai_ism_likelihood / 100, result.edited_metrics.ai_ism_likelihood / 100, result.metric_deltas.ai_ism_pct_change),
    ]
    
    cols = [met_col1, met_col2, met_col3, met_col4]
    
    for col, (name, orig, edit, pct) in zip(cols, metrics_info):
        with col:
            st.markdown(f"**{name}**")
            st.metric(
                label="Original",
                value=f"{orig:.2f}",
            )
            st.metric(
                label="Edited",
                value=f"{edit:.2f}",
                delta=f"{pct:+.0f}%"
            )
    
    # Detailed explanations with tabs
    st.markdown("### Detailed Analysis")
    
    tab_burst, tab_lex, tab_syn, tab_ai = st.tabs(
        ["Burstiness", "Lexical Diversity", "Syntactic Complexity", "AI-ism"]
    )
    
    with tab_burst:
        st.markdown("#### What It Is")
        st.info(
            "**Burstiness** measures sentence length variation. "
            "Low burstiness = uniform sentence lengths (machine-like). "
            "High burstiness = varied sentence lengths (human-like)."
        )
        
        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.burstiness:.3f}")
        with col2:
            st.metric("Edited", f"{result.edited_metrics.burstiness:.3f}", 
                     delta=f"{result.metric_deltas.burstiness_pct_change:+.1f}%")
        
        st.markdown("#### Why It Changed")
        st.success(
            "AI editing standardizes sentence lengths for clarity. "
            "Your sentence variation decreased, indicating more uniform structure."
        )
        
        st.markdown("#### Recommendation")
        st.warning(
            "Consider restoring some of your original sentence variety while keeping AI improvements. "
            "Your authentic voice often includes natural length variation."
        )
    
    with tab_lex:
        st.markdown("#### What It Is")
        st.info(
            "**Lexical Diversity** measures vocabulary richness. "
            "Low diversity = repetitive, formulaic words. "
            "High diversity = varied, rich vocabulary."
        )
        
        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.lexical_diversity:.3f}")
        with col2:
            st.metric("Edited", f"{result.edited_metrics.lexical_diversity:.3f}",
                     delta=f"{result.metric_deltas.lexical_diversity_pct_change:+.1f}%")
        
        st.markdown("#### Why It Changed")
        st.success(
            "AI prefers common academic phrases. "
            "Your vocabulary became less diverse, showing more formulaic word choices."
        )
        
        st.markdown("#### Recommendation")
        st.warning(
            "Keep some of your original less-common vocabulary. "
            "It shows your authentic voice and demonstrates vocabulary growth."
        )
    
    with tab_syn:
        st.markdown("#### What It Is")
        st.info(
            "**Syntactic Complexity** measures sentence structure sophistication. "
            "It includes average sentence length, clause complexity, and modifier density."
        )
        
        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.syntactic_complexity:.3f}")
        with col2:
            st.metric("Edited", f"{result.edited_metrics.syntactic_complexity:.3f}",
                     delta=f"{result.metric_deltas.syntactic_complexity_pct_change:+.1f}%")
        
        st.markdown("#### Why It Changed")
        st.success(
            "AI simplifies syntax for readability. "
            "Your structure became less complex, potentially removing original sophistication."
        )
        
        st.markdown("#### Recommendation")
        st.warning(
            "Review the AI's structural simplifications. "
            "Keep complex sentences that were grammatically correct and show your advancing skills."
        )
    
    with tab_ai:
        st.markdown("#### What It Is")
        st.info(
            "**AI-ism Likelihood** detects phrases and patterns typical of AI-generated text. "
            "Examples: 'it is important to note that', 'delve into', 'in light of'."
        )
        
        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.ai_ism_likelihood:.0f}")
        with col2:
            st.metric("Edited", f"{result.edited_metrics.ai_ism_likelihood:.0f}",
                     delta=f"{result.metric_deltas.ai_ism_pct_change:+.1f}%")
        
        st.markdown("#### AI-isms Detected")
        if result.ai_isms:
            for ai_ism in result.ai_isms[:5]:
                with st.expander(f"📌 {ai_ism['phrase']} ({ai_ism['category']})"):
                    st.markdown(f"**Category**: {ai_ism['category']}")
                    st.markdown(f"**Context**: _{ai_ism['context']}_")
        else:
            st.success("No major AI-isms detected")
        
        st.markdown("#### Recommendation")
        st.warning(
            "High AI-ism scores mean your text relies on AI-generated patterns. "
            "Revert some suggestions, especially openings and closings where your voice matters most."
        )


# ============================================================================
# STEP 3: VISUALIZATIONS (Placeholder for now)
# ============================================================================
def render_step_3_visualize():
    """Step 3: Visual analysis."""
    st.title("📈 Step 3: Visual Analysis")
    
    if 'analysis_result' not in st.session_state:
        st.warning("⚠️ Please complete Step 1 first.")
        return
    
    result = st.session_state.analysis_result
    
    st.markdown("### Chart Comparison")
    st.info("📊 Charts will be displayed here (implemented in Phase 5)")
    
    # Placeholder for visualizations
    st.markdown("**Planned visualizations:**")
    st.markdown("""
    - 6-axis Radar chart (Original vs Edited)
    - Bar chart comparison
    - Side-by-side text diff
    - Time-series (if multiple analyses)
    """)


# ============================================================================
# STEP 4: EXPORT
# ============================================================================
def render_step_4_export():
    """Step 4: Report generation and export."""
    st.title("📄 Step 4: Export Report")
    
    if 'analysis_result' not in st.session_state:
        st.warning("⚠️ Please complete Step 1 first.")
        return
    
    st.markdown("""
    Export your analysis in multiple formats suitable for different purposes:
    """)
    
    export_formats = [
        ("📄 PDF Report", "Professional 17-page report with charts and branding", "pdf"),
        ("📊 Excel Workbook", "5 sheets with data, charts, and analysis-ready format", "xlsx"),
        ("📝 Word Document", "Editable report with track changes and comments", "docx"),
        ("🎬 PowerPoint", "9 slides for presentations with speaker notes", "pptx"),
        ("📈 PNG Charts", "Individual charts for papers and presentations", "png"),
        ("📦 ZIP Bundle", "All charts and documentation for publication", "zip"),
        ("📊 CSV Data", "Raw data for statistical analysis (SPSS, R, Python)", "csv"),
        ("🔗 JSON Data", "Structured data for programmatic access", "json"),
    ]
    
    st.markdown("### Select Format")
    selected_format = st.radio(
        "Choose export format:",
        options=[fmt[2] for fmt in export_formats],
        format_func=lambda x: next(f[0] + ": " + f[1] for f in export_formats if f[2] == x),
        key="export_format"
    )
    
    st.markdown("### Customization Options")
    
    col1, col2 = st.columns(2)
    with col1:
        include_original = st.checkbox("Include original text", value=True)
        include_edited = st.checkbox("Include edited text", value=True)
        include_charts = st.checkbox("Include visualizations", value=True)
    
    with col2:
        include_metrics = st.checkbox("Include detailed metrics", value=True)
        include_ai_isms = st.checkbox("Include AI-ism analysis", value=True)
        include_benchmarks = st.checkbox("Include benchmark comparisons", value=True)
    
    st.markdown("---")
    
    if st.button("📥 Generate & Download", type="primary"):
        st.info(f"📥 Export feature will be implemented in Phase 6 ({selected_format.upper()})")


# ============================================================================
# MAIN APP FLOW
# ============================================================================
def main():
    """Main application flow."""
    # Initialize session state
    if 'nav_step' not in st.session_state:
        st.session_state.nav_step = 1
    
    # Setup sidebar
    current_step = setup_sidebar()
    
    # Render appropriate step
    if current_step == 1:
        render_step_1_input()
    elif current_step == 2:
        render_step_2_metrics()
    elif current_step == 3:
        render_step_3_visualize()
    elif current_step == 4:
        render_step_4_export()


if __name__ == "__main__":
    main()
