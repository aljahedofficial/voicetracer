"""
VoiceTracer - Streamlit Web Application

Main entry point. Implements the 4-step dashboard workflow.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
import PyPDF2
from docx import Document
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models import DocumentPair, AnalysisResult, MetricScores, MetricDeltas, Session, DEFAULT_BENCHMARKS
from metric_calculator import MetricCalculationEngine, MetricComparisonEngine, AIismCalculator
from text_processor import TextProcessor
from visualizations import RadarChartGenerator, BarChartGenerator, TextDiffVisualizer, DeltaVisualization, BurstinessVisualization, IndividualMetricCharts
from exporters import ExportFactory, ExportMetadata
import difflib
import html


# ============================================================================
# FILE EXTRACTION FUNCTIONS
# ============================================================================
def _safe_metric(metrics: dict, raw_key: str, fallback_key: str = None, default: float = 0.0) -> float:
    """Return a metric value with a safe fallback for older metric payloads."""
    if not isinstance(metrics, dict):
        return default
    if raw_key in metrics:
        return metrics[raw_key]
    if fallback_key and fallback_key in metrics:
        return metrics[fallback_key]
    return default


def _normalize_standard_value(metric_key: str, value: float) -> float:
    if metric_key == "syntactic_complexity" and value > 1.0:
        return min(value / 30.0, 1.0)
    return value


def _get_calibration_defaults() -> dict:
    benchmarks = {b.name: b for b in DEFAULT_BENCHMARKS}
    human = benchmarks.get("L2 Unassisted Writing")
    ai = benchmarks.get("AI-Edited Text (ChatGPT)")

    defaults = {
        "human": {
            "burstiness": 1.20,
            "lexical_diversity": 0.55,
            "syntactic_complexity": 0.55,
            "ai_ism_likelihood": 5.0,
            "function_word_ratio": 0.50,
            "discourse_marker_density": 8.0,
            "information_density": 0.58,
            "epistemic_hedging": 0.09,
        },
        "ai": {
            "burstiness": 0.80,
            "lexical_diversity": 0.42,
            "syntactic_complexity": 0.55,
            "ai_ism_likelihood": 78.0,
            "function_word_ratio": 0.60,
            "discourse_marker_density": 18.0,
            "information_density": 0.42,
            "epistemic_hedging": 0.04,
        },
    }

    if human:
        defaults["human"].update({
            "burstiness": human.burstiness,
            "lexical_diversity": human.lexical_diversity,
            "syntactic_complexity": _normalize_standard_value("syntactic_complexity", human.syntactic_complexity),
            "ai_ism_likelihood": human.ai_ism_likelihood,
            "function_word_ratio": human.function_word_ratio,
            "discourse_marker_density": human.discourse_marker_density,
            "information_density": human.information_density,
            "epistemic_hedging": human.epistemic_hedging,
        })
    if ai:
        defaults["ai"].update({
            "burstiness": ai.burstiness,
            "lexical_diversity": ai.lexical_diversity,
            "syntactic_complexity": _normalize_standard_value("syntactic_complexity", ai.syntactic_complexity),
            "ai_ism_likelihood": ai.ai_ism_likelihood,
            "function_word_ratio": ai.function_word_ratio,
            "discourse_marker_density": ai.discourse_marker_density,
            "information_density": ai.information_density,
            "epistemic_hedging": ai.epistemic_hedging,
        })

    return defaults


def _get_default_calibration_values() -> dict:
    return _get_calibration_defaults()


def _ensure_calibration_state() -> None:
    if "calibration_values" not in st.session_state:
        st.session_state.calibration_values = _get_calibration_defaults()


def _calibration_specs() -> list[dict]:
    return [
        {"label": "Burstiness", "key": "burstiness", "min": 0.0, "max": 3.0, "step": 0.01, "fmt": "{:.2f}"},
        {"label": "Lexical Diversity", "key": "lexical_diversity", "min": 0.0, "max": 1.0, "step": 0.01, "fmt": "{:.2f}"},
        {"label": "Syntactic Complexity", "key": "syntactic_complexity", "min": 0.0, "max": 1.0, "step": 0.01, "fmt": "{:.2f}"},
        {"label": "AI-ism Likelihood", "key": "ai_ism_likelihood", "min": 0.0, "max": 100.0, "step": 1.0, "fmt": "{:.0f}"},
        {"label": "Function Word Ratio", "key": "function_word_ratio", "min": 0.0, "max": 1.0, "step": 0.01, "fmt": "{:.2f}"},
        {"label": "Discourse Marker Density", "key": "discourse_marker_density", "min": 0.0, "max": 30.0, "step": 0.5, "fmt": "{:.1f}"},
        {"label": "Information Density", "key": "information_density", "min": 0.0, "max": 1.0, "step": 0.01, "fmt": "{:.2f}"},
        {"label": "Epistemic Hedging", "key": "epistemic_hedging", "min": 0.0, "max": 0.30, "step": 0.01, "fmt": "{:.2f}"},
    ]


def render_calibration_panel(panel_key: str, expanded: bool = False) -> dict:
    _ensure_calibration_state()
    calib = st.session_state.calibration_values
    defaults = _get_default_calibration_values()

    with st.expander("Manual Calibration", expanded=expanded):
        st.caption(
            "Adjust the standard values used for human writing and AI-generated writing. "
            "Settings are saved for this session only."
        )

        if st.button("Reset to defaults", key=f"{panel_key}_reset"):
            defaults = _get_calibration_defaults()
            st.session_state.calibration_values = defaults
            for spec in _calibration_specs():
                st.session_state[f"{panel_key}_human_{spec['key']}"] = float(
                    defaults["human"][spec["key"]]
                )
                st.session_state[f"{panel_key}_ai_{spec['key']}"] = float(
                    defaults["ai"][spec["key"]]
                )
            st.rerun()

        updated_human = {}
        updated_ai = {}
        for spec in _calibration_specs():
            default_human = spec["fmt"].format(defaults["human"].get(spec["key"], 0.0))
            default_ai = spec["fmt"].format(defaults["ai"].get(spec["key"], 0.0))
            col1, col2 = st.columns(2)
            with col1:
                updated_human[spec["key"]] = st.slider(
                    f"{spec['label']} (Human standard) (default: {default_human})",
                    min_value=spec["min"],
                    max_value=spec["max"],
                    value=float(calib["human"][spec["key"]]),
                    step=spec["step"],
                    key=f"{panel_key}_human_{spec['key']}",
                )
            with col2:
                updated_ai[spec["key"]] = st.slider(
                    f"{spec['label']} (AI standard) (default: {default_ai})",
                    min_value=spec["min"],
                    max_value=spec["max"],
                    value=float(calib["ai"][spec["key"]]),
                    step=spec["step"],
                    key=f"{panel_key}_ai_{spec['key']}",
                )

        st.session_state.calibration_values = {
            "human": updated_human,
            "ai": updated_ai,
        }

    return st.session_state.calibration_values


def render_standard_legend(metric_key: str, label: str, fmt: str) -> None:
    _ensure_calibration_state()
    human_val = st.session_state.calibration_values["human"].get(metric_key, 0.0)
    ai_val = st.session_state.calibration_values["ai"].get(metric_key, 0.0)
    st.caption(
        f"Standard values for {label}: Human writing = {fmt.format(human_val)}, "
        f"AI-generated writing = {fmt.format(ai_val)}"
    )


def render_standard_legend_table(title: str = "Standard Values Legend") -> None:
    _ensure_calibration_state()
    rows = []
    for spec in _calibration_specs():
        metric_key = spec["key"]
        rows.append({
            "Metric": spec["label"],
            "Human writing": spec["fmt"].format(
                st.session_state.calibration_values["human"].get(metric_key, 0.0)
            ),
            "AI-generated writing": spec["fmt"].format(
                st.session_state.calibration_values["ai"].get(metric_key, 0.0)
            ),
        })
    st.markdown(f"#### {title}")
    st.table(rows)


def render_global_standard_table(title: str = "Global Standard Values") -> None:
    defaults = _get_default_calibration_values()
    rows = []
    for spec in _calibration_specs():
        metric_key = spec["key"]
        rows.append({
            "Metric": spec["label"],
            "Human writing": spec["fmt"].format(defaults["human"].get(metric_key, 0.0)),
            "AI-generated writing": spec["fmt"].format(defaults["ai"].get(metric_key, 0.0)),
        })
    st.markdown(f"#### {title}")
    st.table(rows)


def _score_against_standards(value: float, human: float, ai: float) -> float:
    if human == ai:
        return 0.5
    score = (value - ai) / (human - ai)
    return max(0.0, min(score, 1.0))


def _label_from_score(score: float) -> str:
    if score >= 0.66:
        return "Human-like"
    if score >= 0.33:
        return "Moderate"
    return "AI-like"


def _final_verdict_from_scores(original_score: float, edited_score: float, threshold: float = 0.05) -> str:
    if edited_score < (original_score - threshold):
        return "Voice shift detected"
    return "Authorial voice retained"


def _build_metric_verdicts(result: AnalysisResult, calibration_payload: dict, threshold: float = 0.05) -> dict:
    verdicts = {}
    adjusted = calibration_payload.get("adjusted", {})
    human = adjusted.get("human", {})
    ai = adjusted.get("ai", {})

    for spec in _calibration_specs():
        key = spec["key"]
        orig_val = getattr(result.original_metrics, key)
        edit_val = getattr(result.edited_metrics, key)
        human_val = human.get(key, 0.0)
        ai_val = ai.get(key, 0.0)

        orig_score = _score_against_standards(orig_val, human_val, ai_val)
        edit_score = _score_against_standards(edit_val, human_val, ai_val)
        verdicts[key] = _final_verdict_from_scores(orig_score, edit_score, threshold=threshold)

    return verdicts


def _render_next_step_button(current_step: int, is_ready: bool = True) -> None:
    def _request_step(step: int) -> None:
        st.session_state["pending_nav_step"] = step

    label = "Go to Next Step →"
    if current_step < 4:
        st.button(
            label,
            key=f"next_step_{current_step}",
            disabled=not is_ready,
            on_click=_request_step,
            args=(current_step + 1,),
        )
        if not is_ready:
            st.caption("Complete the current step to continue.")
    else:
        st.button(label, key="next_step_4", disabled=True)
        st.caption("You're on the final step.")


def _build_calibration_payload(result: AnalysisResult) -> dict:
    _ensure_calibration_state()
    default_vals = _get_default_calibration_values()
    adjusted_vals = st.session_state.calibration_values

    scores_default = {"original": {}, "edited": {}}
    scores_adjusted = {"original": {}, "edited": {}}
    labels_default = {"original": {}, "edited": {}}
    labels_adjusted = {"original": {}, "edited": {}}
    impact = {"original": {}, "edited": {}}

    for spec in _calibration_specs():
        key = spec["key"]
        orig_val = getattr(result.original_metrics, key)
        edit_val = getattr(result.edited_metrics, key)

        default_human = default_vals["human"][key]
        default_ai = default_vals["ai"][key]
        adjusted_human = adjusted_vals["human"][key]
        adjusted_ai = adjusted_vals["ai"][key]

        default_orig_score = _score_against_standards(orig_val, default_human, default_ai)
        default_edit_score = _score_against_standards(edit_val, default_human, default_ai)
        adjusted_orig_score = _score_against_standards(orig_val, adjusted_human, adjusted_ai)
        adjusted_edit_score = _score_against_standards(edit_val, adjusted_human, adjusted_ai)

        scores_default["original"][key] = default_orig_score
        scores_default["edited"][key] = default_edit_score
        scores_adjusted["original"][key] = adjusted_orig_score
        scores_adjusted["edited"][key] = adjusted_edit_score

        labels_default["original"][key] = _label_from_score(default_orig_score)
        labels_default["edited"][key] = _label_from_score(default_edit_score)
        labels_adjusted["original"][key] = _label_from_score(adjusted_orig_score)
        labels_adjusted["edited"][key] = _label_from_score(adjusted_edit_score)

        impact["original"][key] = adjusted_orig_score - default_orig_score
        impact["edited"][key] = adjusted_edit_score - default_edit_score

    return {
        "default": default_vals,
        "adjusted": adjusted_vals,
        "scores": {
            "default": scores_default,
            "adjusted": scores_adjusted,
        },
        "labels": {
            "default": labels_default,
            "adjusted": labels_adjusted,
        },
        "impact": impact,
        "notes": {
            "scale": "Scores are normalized to 0-1 where 1.0 is closer to human standards and 0.0 is closer to AI standards.",
            "impact": "Impact shows adjusted score minus default score for each metric.",
        },
    }


def extract_text_from_txt(file) -> str:
    """Extract text from TXT file."""
    return file.read().decode('utf-8')

def extract_text_from_pdf(file) -> str:
    """Extract text from PDF file using PyPDF2."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text if text.strip() else "[Warning: PDF text extraction failed. Try OCR or manual copy.]"
    except Exception as e:
        return f"[Error extracting PDF: {str(e)}]"

def extract_text_from_docx(file) -> str:
    """Extract text from DOCX file."""
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"[Error extracting DOCX: {str(e)}]"


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

    /* Sidebar collapse button label */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        width: auto;
        min-width: 3.2rem;
        padding-right: 0.6rem;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        overflow: visible;
    }

    button[data-testid="stSidebarCollapseButton"]::after,
    button[data-testid="stSidebarCollapsedControl"]::after,
    [data-testid="stSidebarCollapseButton"] button::after,
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "Menu";
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR NAVIGATION & SETUP
# ============================================================================
def setup_sidebar():
    """Setup sidebar navigation and settings."""
    with st.sidebar:
        st.markdown("## 🎙️ VoiceTracer")
        st.caption("Build: V1-09-02-26'")
        st.markdown("---")
        
        st.markdown("### About")
        st.info(
            "VoiceTracer measures stylistic changes when L2 writers use AI editing tools. "
            "Compare your original and edited texts to understand voice preservation."
        )

        with st.expander("Metric Definitions", expanded=False):
            _ensure_calibration_state()
            defaults = _get_default_calibration_values()
            current = st.session_state.calibration_values

            st.markdown(
                """
**Burstiness**: std dev of sentence length divided by mean length.  
**Lexical Diversity**: MTLD scaled to 0-1.  
**Syntactic Complexity**: 0.4 * ASL + 0.3 * subordination + 0.3 * modifier density.  
**AI-ism Likelihood**: phrase-pattern score scaled 0-100.  
**Function Word Ratio**: function words / total words.  
**Discourse Marker Density**: markers per 1,000 words.  
**Information Density**: content-word and proper-noun signals (0-1).  
**Epistemic Hedging**: hedging markers per word (0-1).
"""
            )

            st.markdown("**Standards (Human vs AI)**")
            rows = []
            for spec in _calibration_specs():
                key = spec["key"]
                rows.append({
                    "Metric": spec["label"],
                    "Human (default)": spec["fmt"].format(defaults["human"].get(key, 0.0)),
                    "AI (default)": spec["fmt"].format(defaults["ai"].get(key, 0.0)),
                    "Human (current)": spec["fmt"].format(current["human"].get(key, 0.0)),
                    "AI (current)": spec["fmt"].format(current["ai"].get(key, 0.0)),
                })
            st.table(rows)

        with st.expander("Metric Calculations", expanded=False):
            st.markdown(
                """
**Burstiness**  
Formula: $\sigma(\text{sentence length}) / \mu(\text{sentence length})$  
Why it matters: Captures natural rhythm and variation; low values often indicate uniform, AI-like structure.

**Lexical Diversity**  
Formula: MTLD scaled to $0-1$ (higher = more varied vocabulary).  
Why it matters: Shows how rich and non-repetitive the word choice is.

**Syntactic Complexity**  
Formula: $0.4 \cdot \text{ASL} + 0.3 \cdot \text{Subordination} + 0.3 \cdot \text{Modifier Density}$, normalized.  
Why it matters: Measures structural sophistication beyond simple sentence length.

**AI-ism Likelihood**  
Formula: Pattern-frequency score scaled to $0-100$.  
Why it matters: Detects formulaic phrases and patterns typical of AI-generated text.

**Function Word Ratio**  
Formula: $\text{function words} / \text{total words}$.  
Why it matters: High ratios can indicate over-scaffolded, AI-smoothed writing.

**Discourse Marker Density**  
Formula: $\text{markers per 1,000 words}$.  
Why it matters: Excessive signposting can signal AI-style editing.

**Information Density**  
Formula: Content-word and proper-noun signals scaled to $0-1$.  
Why it matters: Low values suggest verbose, generic language.

**Epistemic Hedging**  
Formula: $\text{hedging markers} / \text{total words}$, scaled to $0-1$.  
Why it matters: Human writing often hedges; AI text tends to sound overly certain.
"""
            )
            st.markdown(
                "Full documentation: [prototype.txt](prototype.txt)"
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
        st.markdown("""
        **Developer:**  
        Architect & Prompt Engineer: Minhaj Al Jahed  
        AI Engineering Support: GitHub Copilot Pro  
        Autocompletion & Debugging: GitHub Codespaces
        """)
        components.html(
            """
            <script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>
                        <style>
                            .vt-profile-link {
                                display: inline-flex;
                                align-items: center;
                                gap: 6px;
                                text-decoration: none;
                                font-weight: 600;
                                color: #000080;
                            }
                            .vt-profile-link:hover {
                                text-decoration: underline;
                            }
                            .vt-linkedin-icon {
                                width: 16px;
                                height: 16px;
                                fill: #0a66c2;
                            }
                            .vt-researchgate-icon {
                                width: 16px;
                                height: 16px;
                                fill: #00ccbb;
                            }
                            .vt-x-icon {
                                width: 16px;
                                height: 16px;
                                fill: #111111;
                            }
                        </style>
                        <div style="margin-bottom: 8px;">
                            <a class="vt-profile-link vt-linkedin-link" href="https://bd.linkedin.com/in/minhaj10" target="_blank" rel="noopener noreferrer">
                                <svg class="vt-linkedin-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                                    <path d="M20.45 20.45h-3.56v-5.4c0-1.29-.02-2.96-1.8-2.96-1.8 0-2.08 1.41-2.08 2.87v5.49H9.45V9h3.42v1.56h.05c.48-.9 1.65-1.85 3.39-1.85 3.62 0 4.29 2.38 4.29 5.47v6.27ZM5.34 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14ZM7.12 20.45H3.56V9h3.56v11.45Z"/>
                                </svg>
                                Minhaj Al Jahed
                            </a>
                        </div>
                        <div>
                            <a class="vt-profile-link vt-researchgate-link" href="https://www.researchgate.net/profile/Minhaj-Al-Jahed-2?ev=hdr_xprf" target="_blank" rel="noopener noreferrer">
                                <svg class="vt-researchgate-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                                    <path d="M20.7 10.9c0-3.8-3.2-6.9-7.1-6.9H7.3C5 4 3.1 5.9 3.1 8.2V16c0 2.2 1.8 4 4.1 4h7.6c3.2 0 5.9-2.5 5.9-5.6 0-1.2-.4-2.3-1.1-3.1.7-.8 1.1-1.9 1.1-3.4ZM7.3 7h6.2c2.2 0 4 1.7 4 3.9 0 1.8-1.2 3.1-3 3.1h-4.6v-2.1h3.6c1 0 1.6-.6 1.6-1.4 0-.9-.7-1.6-1.7-1.6H7.3C6.6 9 6 9.6 6 10.3v5.8c0 .7.6 1.3 1.3 1.3h7.6c1.6 0 2.9-1.2 2.9-2.8 0-1.2-.7-2.2-2.1-2.2h-3.5v-2.1h4c2 0 2.5-1.2 2.5-2.4 0-1.7-1.5-2.9-3.2-2.9H7.3Z"/>
                                </svg>
                                Minhaj Al Jahed
                            </a>
                        </div>
                        <div style="margin-top: 6px;">
                            <a class="vt-profile-link vt-x-link" href="https://x.com/MinhajAl51253" target="_blank" rel="noopener noreferrer">
                                <svg class="vt-x-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                                    <path d="M18.9 2H22l-7.2 8.2L23 22h-6.7l-5.2-6.8L5.2 22H2l7.7-8.8L1 2h6.8l4.7 6.1L18.9 2Zm-1.2 18h1.8L7.3 4H5.3l12.4 16Z"/>
                                </svg>
                                Minhaj Al Jahed
                            </a>
                        </div>
            """,
            height=320,
        )
        
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

    render_calibration_panel("step1_calibration", expanded=False)
    with st.expander(
        "What is currently set by the user for Human vs AI Standard Values",
        expanded=False,
    ):
        render_standard_legend_table(
            "What is currently set by the user for Human vs AI Standard Values"
        )
    with st.expander(
        "What actually is set globally (default values)",
        expanded=False,
    ):
        render_global_standard_table(
            "What actually is set globally (default values)"
        )
    st.markdown("---")
    
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
    st.markdown("*Supports: TXT, PDF (text extraction), DOCX, DOC*")
    col1_up, col2_up = st.columns(2)
    
    with col1_up:
        orig_file = st.file_uploader("Upload original text", key="orig_file", type=['txt', 'pdf', 'docx', 'doc'])
        if orig_file:
            file_ext = orig_file.name.split('.')[-1].lower()
            try:
                if file_ext == 'txt':
                    original_text = extract_text_from_txt(orig_file)
                elif file_ext == 'pdf':
                    original_text = extract_text_from_pdf(orig_file)
                elif file_ext in ['docx', 'doc']:
                    original_text = extract_text_from_docx(orig_file)
            except Exception as e:
                st.error(f"Failed to extract text: {str(e)}")
    
    with col2_up:
        edit_file = st.file_uploader("Upload edited text", key="edit_file", type=['txt', 'pdf', 'docx', 'doc'])
        if edit_file:
            file_ext = edit_file.name.split('.')[-1].lower()
            try:
                if file_ext == 'txt':
                    edited_text = extract_text_from_txt(edit_file)
                elif file_ext == 'pdf':
                    edited_text = extract_text_from_pdf(edit_file)
                elif file_ext in ['docx', 'doc']:
                    edited_text = extract_text_from_docx(edit_file)
            except Exception as e:
                st.error(f"Failed to extract text: {str(e)}")
    
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
                    burstiness=_safe_metric(orig_metrics, 'burstiness_raw', 'burstiness'),
                    lexical_diversity=_safe_metric(orig_metrics, 'lexical_diversity_raw', 'lexical_diversity'),
                    syntactic_complexity=_safe_metric(orig_metrics, 'syntactic_complexity_raw', 'syntactic_complexity'),
                    ai_ism_likelihood=_safe_metric(orig_metrics, 'ai_ism_likelihood_raw', 'ai_ism_likelihood'),
                    function_word_ratio=_safe_metric(orig_metrics, 'function_word_ratio_raw', 'function_word_ratio'),
                    discourse_marker_density=_safe_metric(orig_metrics, 'discourse_marker_density_raw', 'discourse_marker_density'),
                    information_density=_safe_metric(orig_metrics, 'information_density_raw', 'information_density'),
                    epistemic_hedging=_safe_metric(orig_metrics, 'epistemic_hedging_raw', 'epistemic_hedging'),
                )
                
                metric_scores_edit = MetricScores(
                    burstiness=_safe_metric(edit_metrics, 'burstiness_raw', 'burstiness'),
                    lexical_diversity=_safe_metric(edit_metrics, 'lexical_diversity_raw', 'lexical_diversity'),
                    syntactic_complexity=_safe_metric(edit_metrics, 'syntactic_complexity_raw', 'syntactic_complexity'),
                    ai_ism_likelihood=_safe_metric(edit_metrics, 'ai_ism_likelihood_raw', 'ai_ism_likelihood'),
                    function_word_ratio=_safe_metric(edit_metrics, 'function_word_ratio_raw', 'function_word_ratio'),
                    discourse_marker_density=_safe_metric(edit_metrics, 'discourse_marker_density_raw', 'discourse_marker_density'),
                    information_density=_safe_metric(edit_metrics, 'information_density_raw', 'information_density'),
                    epistemic_hedging=_safe_metric(edit_metrics, 'epistemic_hedging_raw', 'epistemic_hedging'),
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
                    function_word_ratio_delta=deltas['function_word_ratio_delta'],
                    function_word_ratio_pct_change=deltas['function_word_ratio_pct_change'],
                    discourse_marker_density_delta=deltas['discourse_marker_density_delta'],
                    discourse_marker_density_pct_change=deltas['discourse_marker_density_pct_change'],
                    information_density_delta=deltas['information_density_delta'],
                    information_density_pct_change=deltas['information_density_pct_change'],
                    epistemic_hedging_delta=deltas['epistemic_hedging_delta'],
                    epistemic_hedging_pct_change=deltas['epistemic_hedging_pct_change'],
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
                st.session_state.orig_metrics = orig_metrics
                st.session_state.edit_metrics = edit_metrics
            
            st.success("✓ Analysis complete! Go to Step 2 to view metrics.")

    st.markdown("---")
    _render_next_step_button(1, is_ready='analysis_result' in st.session_state)


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
    st.markdown("Compare your metrics across 8 core dimensions:")
    
    metrics_info = [
        {
            "name": "Burstiness",
            "orig": result.original_metrics.burstiness,
            "edit": result.edited_metrics.burstiness,
            "delta": result.metric_deltas.burstiness_delta,
            "fmt": "{:.3f}",
            "delta_fmt": "{:+.3f}",
        },
        {
            "name": "Lexical Diversity",
            "orig": result.original_metrics.lexical_diversity,
            "edit": result.edited_metrics.lexical_diversity,
            "delta": result.metric_deltas.lexical_diversity_delta,
            "fmt": "{:.3f}",
            "delta_fmt": "{:+.3f}",
        },
        {
            "name": "Syntactic Complexity",
            "orig": result.original_metrics.syntactic_complexity,
            "edit": result.edited_metrics.syntactic_complexity,
            "delta": result.metric_deltas.syntactic_complexity_delta,
            "fmt": "{:.3f}",
            "delta_fmt": "{:+.3f}",
        },
        {
            "name": "AI-ism Likelihood",
            "orig": result.original_metrics.ai_ism_likelihood,
            "edit": result.edited_metrics.ai_ism_likelihood,
            "delta": result.metric_deltas.ai_ism_delta,
            "fmt": "{:.1f}",
            "delta_fmt": "{:+.1f}",
        },
        {
            "name": "Function Word Ratio",
            "orig": result.original_metrics.function_word_ratio,
            "edit": result.edited_metrics.function_word_ratio,
            "delta": result.metric_deltas.function_word_ratio_delta,
            "fmt": "{:.3f}",
            "delta_fmt": "{:+.3f}",
        },
        {
            "name": "Discourse Marker Density",
            "orig": result.original_metrics.discourse_marker_density,
            "edit": result.edited_metrics.discourse_marker_density,
            "delta": result.metric_deltas.discourse_marker_density_delta,
            "fmt": "{:.2f}",
            "delta_fmt": "{:+.2f}",
        },
        {
            "name": "Information Density",
            "orig": result.original_metrics.information_density,
            "edit": result.edited_metrics.information_density,
            "delta": result.metric_deltas.information_density_delta,
            "fmt": "{:.3f}",
            "delta_fmt": "{:+.3f}",
        },
        {
            "name": "Epistemic Hedging",
            "orig": result.original_metrics.epistemic_hedging,
            "edit": result.edited_metrics.epistemic_hedging,
            "delta": result.metric_deltas.epistemic_hedging_delta,
            "fmt": "{:.3f}",
            "delta_fmt": "{:+.3f}",
        },
    ]
    
    for row in range(2):
        cols = st.columns(4)
        for col, metric in zip(cols, metrics_info[row * 4:(row + 1) * 4]):
            with col:
                st.markdown(f"**{metric['name']}**")
                st.metric(
                    label="Original",
                    value=metric["fmt"].format(metric["orig"]),
                )
                st.metric(
                    label="Edited",
                    value=metric["fmt"].format(metric["edit"]),
                    delta=metric["delta_fmt"].format(metric["delta"]),
                )
    
    # Detailed explanations with tabs
    st.markdown("### Calibration-Based Scores")
    calibration_payload = _build_calibration_payload(result)
    st.caption(calibration_payload["notes"]["scale"])
    verdicts = _build_metric_verdicts(result, calibration_payload)

    def render_calibration_table(title: str, scores: dict, labels: dict) -> None:
        rows = []
        for spec in _calibration_specs():
            key = spec["key"]
            rows.append({
                "Metric": spec["label"],
                "Original score": f"{scores['original'][key]:.2f}",
                "Original label": labels["original"][key],
                "Edited score": f"{scores['edited'][key]:.2f}",
                "Edited label": labels["edited"][key],
            })
        st.table(rows)

    with st.expander("Default Calibration (no manual adjustments)", expanded=False):
        render_calibration_table(
            "Default Calibration (no manual adjustments)",
            calibration_payload["scores"]["default"],
            calibration_payload["labels"]["default"],
        )
    with st.expander("Adjusted Calibration (manual settings)", expanded=False):
        render_calibration_table(
            "Adjusted Calibration (manual settings)",
            calibration_payload["scores"]["adjusted"],
            calibration_payload["labels"]["adjusted"],
        )

    impact_rows = []
    for spec in _calibration_specs():
        key = spec["key"]
        impact_rows.append({
            "Metric": spec["label"],
            "Original score Δ": f"{calibration_payload['impact']['original'][key]:+.2f}",
            "Edited score Δ": f"{calibration_payload['impact']['edited'][key]:+.2f}",
        })
    with st.expander("Calibration Impact (Adjusted - Default)", expanded=False):
        st.table(impact_rows)

    st.caption(calibration_payload["notes"]["impact"])

    # Detailed explanations with tabs
    st.markdown("### Detailed Analysis")
    
    tab_burst, tab_lex, tab_syn, tab_ai, tab_fwr, tab_dmd, tab_id, tab_hedge = st.tabs(
        [
            "Burstiness",
            "Lexical Diversity",
            "Syntactic Complexity",
            "AI-ism",
            "Function Words",
            "Discourse Markers",
            "Information Density",
            "Hedging",
        ]
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
                     delta=f"{result.metric_deltas.burstiness_delta:+.3f}")

        
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

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['burstiness']}**")
    
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
                     delta=f"{result.metric_deltas.lexical_diversity_delta:+.3f}")

        
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

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['lexical_diversity']}**")
    
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
                     delta=f"{result.metric_deltas.syntactic_complexity_delta:+.3f}")

        
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

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['syntactic_complexity']}**")
    
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
                     delta=f"{result.metric_deltas.ai_ism_delta:+.1f}")

        
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

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['ai_ism_likelihood']}**")

    with tab_fwr:
        st.markdown("#### What It Is")
        st.info(
            "**Function Word Ratio** measures how much grammatical scaffolding "
            "(articles, prepositions, pronouns) appears in your text."
        )

        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.function_word_ratio:.3f}")
        with col2:
            st.metric(
                "Edited",
                f"{result.edited_metrics.function_word_ratio:.3f}",
                delta=f"{result.metric_deltas.function_word_ratio_delta:+.3f}",
            )


        st.markdown("#### Why It Changed")
        st.success(
            "AI editors tend to add function words to smooth flow and grammar. "
            "A rising ratio suggests more scaffolding and less dense wording."
        )

        st.markdown("#### Recommendation")
        st.warning(
            "If the ratio rose, the edited text may be over-scaffolded. "
            "Consider tightening phrases or restoring content-heavy wording."
        )

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['function_word_ratio']}**")

    with tab_dmd:
        st.markdown("#### What It Is")
        st.info(
            "**Discourse Marker Density** counts explicit connectors like "
            "'moreover' and 'therefore' per 1,000 words."
        )

        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.discourse_marker_density:.2f}")
        with col2:
            st.metric(
                "Edited",
                f"{result.edited_metrics.discourse_marker_density:.2f}",
                delta=f"{result.metric_deltas.discourse_marker_density_delta:+.2f}",
            )


        st.markdown("#### Why It Changed")
        st.success(
            "AI editing often inserts explicit connectors to guide readers. "
            "Higher density signals more signposting and a more formulaic flow."
        )

        st.markdown("#### Recommendation")
        st.warning(
            "If density increased, consider removing repetitive connectors "
            "and letting ideas flow without constant signposting."
        )

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['discourse_marker_density']}**")

    with tab_id:
        st.markdown("#### What It Is")
        st.info(
            "**Information Density** estimates specificity per word using content words "
            "and proper-noun signals."
        )

        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.information_density:.3f}")
        with col2:
            st.metric(
                "Edited",
                f"{result.edited_metrics.information_density:.3f}",
                delta=f"{result.metric_deltas.information_density_delta:+.3f}",
            )


        st.markdown("#### Why It Changed")
        st.success(
            "AI often expands sentences with generic phrasing. "
            "Lower density means more filler relative to concrete details."
        )

        st.markdown("#### Recommendation")
        st.warning(
            "If density dropped, consider reintroducing concrete details and specific terms."
        )

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['information_density']}**")

    with tab_hedge:
        st.markdown("#### What It Is")
        st.info(
            "**Epistemic Hedging** tracks uncertainty markers (e.g., 'might', 'perhaps'). "
            "Humans hedge more than AI-generated text."
        )

        st.markdown("#### Your Scores")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original", f"{result.original_metrics.epistemic_hedging:.3f}")
        with col2:
            st.metric(
                "Edited",
                f"{result.edited_metrics.epistemic_hedging:.3f}",
                delta=f"{result.metric_deltas.epistemic_hedging_delta:+.3f}",
            )


        st.markdown("#### Why It Changed")
        st.success(
            "AI-generated edits often sound more certain. "
            "A drop in hedging indicates a more confident, less nuanced tone."
        )

        st.markdown("#### Recommendation")
        st.warning(
            "If hedging decreased, consider restoring nuanced language where appropriate."
        )

        st.markdown("#### Final Verdict")
        st.markdown(f"**Final Verdict: {verdicts['epistemic_hedging']}**")

    st.markdown("---")
    _render_next_step_button(2, is_ready=True)


# ============================================================================
# STEP 3: VISUALIZATIONS
# ============================================================================
def render_step_3_visualize():
    """Step 3: Visual analysis with interactive charts."""
    st.title("📈 Step 3: Visual Analysis")
    
    if 'analysis_result' not in st.session_state:
        st.warning("⚠️ Please complete Step 1 first.")
        return
    
    result = st.session_state.analysis_result
    doc_pair = st.session_state.doc_pair
    
    # Select visualization type
    st.markdown("### Choose Your Visualization")
    viz_type = st.radio(
        "Select visualization:",
        options=["radar", "individual", "burstiness", "bars", "deltas", "diff"],
        format_func=lambda x: {
            "radar": "🎯 8-Axis Radar (Original vs Edited)",
            "individual": "📌 Individual Metric Charts",
            "burstiness": "📊 Syntactic Burstiness",
            "bars": "📊 Bar Chart Comparison",
            "deltas": "📈 Metric Changes",
            "diff": "📝 Text Difference Highlight"
        }[x],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Get engine data for visualizations
    # For radar chart (expects non-raw keys)
    radar_orig_metrics = st.session_state.get('orig_metrics', {})
    radar_edited_metrics = st.session_state.get('edit_metrics', {})
    
    # For bar chart (expects _raw keys)
    bar_orig_metrics = st.session_state.get('orig_metrics', {})
    bar_edited_metrics = st.session_state.get('edit_metrics', {})
    
    try:
        if viz_type == "radar":
            st.markdown("### 8-Axis Radar Chart")
            st.markdown("*Compare your original and edited texts across 8 linguistic dimensions*")
            
            fig = RadarChartGenerator.create_metric_radar(radar_orig_metrics, radar_edited_metrics)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### What to Look For")
            st.info(
                "**Green area** = Original text characteristics  \n"
                "**Red area** = AI-edited text characteristics  \n"
                "**Overlap** = Preserved voice  \n"
                "**Divergence** = Loss of voice authenticity"
            )

        elif viz_type == "individual":
            st.markdown("### Individual Metric Charts")
            st.markdown("*Each metric shown as its own comparison chart*")

            panels = IndividualMetricCharts.create_metric_panels(bar_orig_metrics, bar_edited_metrics)
            for idx in range(0, len(panels), 2):
                cols = st.columns(2)
                for col, (_, fig) in zip(cols, panels[idx:idx + 2]):
                    with col:
                        st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "burstiness":
            st.markdown("### Syntactic Burstiness")
            st.markdown("*Word count per sentence reveals writing patterns*")

            threshold_defaults = BurstinessVisualization._get_burstiness_thresholds()
            with st.expander("Heuristic Calibration", expanded=False):
                st.caption(
                    "Adjust thresholds to see how they affect burstiness labeling. "
                    "Changes apply to this view only."
                )
                ai_cutoff_override = st.slider(
                    "CV Threshold (AI cutoff)",
                    min_value=0.0,
                    max_value=1.0,
                    value=threshold_defaults.get("ai_cutoff", 0.34),
                    step=0.01,
                )
                human_cutoff_override = st.slider(
                    "CV Threshold (Human cutoff)",
                    min_value=0.0,
                    max_value=1.0,
                    value=threshold_defaults.get("human_cutoff", 0.45),
                    step=0.01,
                )
                delta_cutoff_override = st.slider(
                    "Calibration Threshold (delta)",
                    min_value=0.0,
                    max_value=0.50,
                    value=threshold_defaults.get("delta_cutoff", 0.08),
                    step=0.01,
                )
                if human_cutoff_override <= ai_cutoff_override:
                    st.warning("Human cutoff should be higher than AI cutoff.")
                st.caption(
                    "Standard: "
                    f"ai_cutoff={threshold_defaults.get('ai_cutoff', 0.34):.2f}, "
                    f"human_cutoff={threshold_defaults.get('human_cutoff', 0.45):.2f}, "
                    f"delta_cutoff={threshold_defaults.get('delta_cutoff', 0.08):.2f}"
                )
            
            # Generate burstiness visualizations
            bar_fig, stats = BurstinessVisualization.create_sentence_length_bars(
                doc_pair.original_text,
                doc_pair.edited_text,
                threshold_overrides={
                    "ai_cutoff": ai_cutoff_override,
                    "human_cutoff": human_cutoff_override,
                    "delta_cutoff": delta_cutoff_override,
                },
            )
            
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Words (Original)", f"{stats['original']['avg_words']:.1f}")
            with col2:
                st.metric("Burstiness (Original)", f"{stats['original']['burstiness_norm']:.2f}")
            with col3:
                st.metric("Avg Words (Edited)", f"{stats['edited']['avg_words']:.1f}")
            with col4:
                st.metric("Burstiness (Edited)", f"{stats['edited']['burstiness_norm']:.2f}")

            min_sentences = min(
                stats['original'].get('sentence_count', 0),
                stats['edited'].get('sentence_count', 0),
            )
            if min_sentences < 5:
                st.warning(
                    "Reliability warning: fewer than 5 sentences detected. "
                    "Burstiness estimates can be unstable for very short texts."
                )
            
            # Pattern analysis
            col_a, col_b = st.columns(2)
            thresholds = stats.get('thresholds', {})
            ai_cutoff = thresholds.get('ai_cutoff', 0.34)
            human_cutoff = thresholds.get('human_cutoff', 0.45)
            delta_cutoff = thresholds.get('delta_cutoff', 0.08)

            with col_a:
                if stats['original']['burstiness_norm'] >= human_cutoff:
                    st.success(f"✓ Original: **{stats['original']['pattern']}**")
                elif stats['original']['burstiness_norm'] >= ai_cutoff:
                    st.warning(f"⚠ Original: **{stats['original']['pattern']}**")
                else:
                    st.error(f"✗ Original: **{stats['original']['pattern']}**")
            
            with col_b:
                burst_delta = stats['edited']['burstiness_norm'] - stats['original']['burstiness_norm']
                if burst_delta <= -delta_cutoff and stats['edited']['burstiness_norm'] < stats['original']['burstiness_norm']:
                    st.error("✗ Edited: **Mixed/AI-edited Pattern**")
                elif stats['edited']['burstiness_norm'] >= human_cutoff:
                    st.success(f"✓ Edited: **{stats['edited']['pattern']}**")
                elif stats['edited']['burstiness_norm'] >= ai_cutoff:
                    st.warning(f"⚠ Edited: **{stats['edited']['pattern']}**")
                else:
                    st.error(f"✗ Edited: **{stats['edited']['pattern']}**")
            
            # Display bar chart
            st.plotly_chart(bar_fig, use_container_width=True)
            
            # Display fluctuation curve
            fluct_fig = BurstinessVisualization.create_fluctuation_curve(
                doc_pair.original_text,
                doc_pair.edited_text
            )
            st.plotly_chart(fluct_fig, use_container_width=True)
            
            # Analysis insight
            st.markdown("### Analysis")
            burstiness_change = stats['edited']['burstiness_norm'] - stats['original']['burstiness_norm']
            if burstiness_change <= -delta_cutoff:
                st.info(
                    f"📉 **Burstiness drop detected**: AI editing reduced burstiness by {abs(burstiness_change):.2f}. "
                    "This indicates more uniform, machine-like sentence structure. Consider restoring some original sentence variety."
                )
            elif burstiness_change < 0:
                st.info(
                    f"📊 **Moderate reduction**: Burstiness decreased by {abs(burstiness_change):.2f}. "
                    "Some natural flow may have been smoothed out by AI editing."
                )
            else:
                st.success(
                    f"📈 **Variation maintained or improved**: Your edited text preserves natural burstiness patterns. "
                    "The editing maintained authentic human-like sentence flow."
                )

            # Threshold transparency
            st.caption(
                f"Thresholds used (normalized): ai_cutoff={ai_cutoff:.2f}, "
                f"human_cutoff={human_cutoff:.2f}, delta_cutoff={delta_cutoff:.2f}"
            )
            st.caption(f"Calibration threshold (delta): {delta_cutoff:.2f}")
        
        elif viz_type == "bars":
            st.markdown("### Metric Comparison (Bar Chart)")
            st.markdown("*Side-by-side comparison of key metrics*")
            
            fig = BarChartGenerator.create_metric_comparison(bar_orig_metrics, bar_edited_metrics)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### Interpretation")
            increases = []
            decreases = []
            
            change_map = [
                ("Burstiness", result.metric_deltas.burstiness_delta, "more varied", "more uniform"),
                ("Lexical Diversity", result.metric_deltas.lexical_diversity_delta, "more varied vocabulary", "more formulaic"),
                ("Syntactic Complexity", result.metric_deltas.syntactic_complexity_delta, "more complex", "more simplified"),
                ("AI-ism Likelihood", result.metric_deltas.ai_ism_delta, "more AI-like", "less AI-like"),
                ("Function Word Ratio", result.metric_deltas.function_word_ratio_delta, "more scaffolded", "more content-heavy"),
                ("Discourse Marker Density", result.metric_deltas.discourse_marker_density_delta, "more signposted", "more implicit"),
                ("Information Density", result.metric_deltas.information_density_delta, "more specific", "more verbose"),
                ("Epistemic Hedging", result.metric_deltas.epistemic_hedging_delta, "more hedged", "more confident"),
            ]
            
            for name, delta, up_label, down_label in change_map:
                if delta > 0:
                    increases.append(f"{name} ({up_label})")
                elif delta < 0:
                    decreases.append(f"{name} ({down_label})")
            
            if decreases:
                st.warning(f"**Metrics that decreased**: {', '.join(decreases)}")
            if increases:
                st.success(f"**Metrics that increased**: {', '.join(increases)}")
        
        elif viz_type == "deltas":
            st.markdown("### Metric Shift Visualization")
            st.markdown("*Absolute shift for each metric from original to edited*")
            
            # Create deltas dict in expected format
            deltas_dict = {
                'burstiness_pct_change': result.metric_deltas.burstiness_pct_change,
                'lexical_diversity_pct_change': result.metric_deltas.lexical_diversity_pct_change,
                'syntactic_complexity_pct_change': result.metric_deltas.syntactic_complexity_pct_change,
                'ai_ism_likelihood_pct_change': result.metric_deltas.ai_ism_pct_change,
                'function_word_ratio_pct_change': result.metric_deltas.function_word_ratio_pct_change,
                'discourse_marker_density_pct_change': result.metric_deltas.discourse_marker_density_pct_change,
                'information_density_pct_change': result.metric_deltas.information_density_pct_change,
                'epistemic_hedging_pct_change': result.metric_deltas.epistemic_hedging_pct_change,
            }
            
            fig = DeltaVisualization.create_delta_chart(deltas_dict)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### Summary of Changes")
            
            metrics_summary = [
                ("Burstiness", result.metric_deltas.burstiness_delta, "sentence variation"),
                ("Lexical Diversity", result.metric_deltas.lexical_diversity_delta, "vocabulary richness"),
                ("Syntactic Complexity", result.metric_deltas.syntactic_complexity_delta, "structure sophistication"),
                ("AI-ism Likelihood", result.metric_deltas.ai_ism_delta, "AI-pattern frequency"),
                ("Function Word Ratio", result.metric_deltas.function_word_ratio_delta, "grammatical scaffolding"),
                ("Discourse Marker Density", result.metric_deltas.discourse_marker_density_delta, "explicit signposting"),
                ("Information Density", result.metric_deltas.information_density_delta, "content specificity"),
                ("Epistemic Hedging", result.metric_deltas.epistemic_hedging_delta, "uncertainty markers"),
            ]
            
            for name, delta, description in metrics_summary:
                if delta < 0:
                    st.error(f"⬇️ **{name}** decreased {abs(delta):.3f} ({description})")
                elif delta > 0:
                    st.warning(f"⬆️ **{name}** increased {delta:.3f} ({description})")
                else:
                    st.info(f"→ **{name}** remained stable ({description})")
        
        elif viz_type == "diff":
            st.markdown("### Text Difference Highlight")
            st.markdown("*Original text (green) vs Edited text (red) - showing changes*")
            
            # Create diff
            original_words = doc_pair.original_text.split()
            edited_words = doc_pair.edited_text.split()
            
            differ = difflib.SequenceMatcher(None, original_words, edited_words)
            
            col1, col2 = st.columns(2)
            
            def _render_words(words: list[str]) -> str:
                return " ".join(html.escape(w) for w in words)

            with col1:
                st.markdown("#### Original")
                original_html = '<div style="padding: 15px; background: #f0f0f0; border-radius: 5px; max-height: 400px; overflow-y: auto;">'
                for tag, i1, i2, j1, j2 in differ.get_opcodes():
                    if tag == 'equal':
                        original_html += _render_words(original_words[i1:i2]) + ' '
                    elif tag == 'delete':
                        original_html += f'<mark style="background: #90EE90;">{_render_words(original_words[i1:i2])}</mark> '
                    elif tag == 'replace':
                        original_html += f'<mark style="background: #FFE08A;">{_render_words(original_words[i1:i2])}</mark> '
                original_html += '</div>'
                st.markdown(original_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### Edited")
                edited_html = '<div style="padding: 15px; background: #f0f0f0; border-radius: 5px; max-height: 400px; overflow-y: auto;">'
                for tag, i1, i2, j1, j2 in differ.get_opcodes():
                    if tag == 'equal':
                        edited_html += _render_words(edited_words[j1:j2]) + ' '
                    elif tag == 'insert':
                        edited_html += f'<mark style="background: #FFB6C1;">{_render_words(edited_words[j1:j2])}</mark> '
                    elif tag == 'replace':
                        edited_html += f'<mark style="background: #FFD1B3;">{_render_words(edited_words[j1:j2])}</mark> '
                edited_html += '</div>'
                st.markdown(edited_html, unsafe_allow_html=True)
            
            st.markdown("**Legend**: 🟢 Original removed, 🟠 Original replaced, 🔴 AI-edited added, 🟤 AI-edited replaced")
    
    except Exception as e:
        st.error(f"Error generating visualization: {str(e)}")
        st.info("The visualization modules are working, but there may be data format issues.")

    st.markdown("---")
    _render_next_step_button(3, is_ready=True)


# ============================================================================
# STEP 4: EXPORT
# ============================================================================
def render_step_4_export():
    """Step 4: Report generation and export."""
    st.title("📄 Step 4: Export Report")
    
    if 'analysis_result' not in st.session_state:
        st.warning("⚠️ Please complete Step 1 first.")
        return
    
    result = st.session_state.analysis_result
    doc_pair = st.session_state.doc_pair
    
    st.markdown("""
    Export your analysis in multiple formats suitable for different purposes:
    """)
    
    export_formats = [
        ("📊 CSV Data", "Raw data for statistical analysis (SPSS, R, Python)", "csv"),
        ("🔗 JSON Data", "Structured data for programmatic access", "json"),
        ("📝 Word Document", "Editable report with your analysis", "docx"),
        ("📈 Excel Workbook", "Spreadsheet with metrics and data", "xlsx"),
        ("📄 PDF Report", "Professional formatted report", "pdf"),
    ]
    
    # Create format options dict for display
    format_options = {fmt[2]: f"{fmt[0]}\n{fmt[1]}" for fmt in export_formats}
    
    st.markdown("### Select Format")
    selected_format = st.radio(
        "Choose export format:",
        options=[fmt[2] for fmt in export_formats],
        format_func=lambda x: format_options[x],
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
        with st.spinner("Processing. Just a minute."):
            try:
                calibration_payload = _build_calibration_payload(result)
                # Calculate text metadata
                orig_metadata = {
                    'word_count': len(doc_pair.original_text.split()),
                    'character_count': len(doc_pair.original_text),
                    'sentence_count': len([s for s in doc_pair.original_text.split('.') if s.strip()]),
                    'avg_word_length': sum(len(w) for w in doc_pair.original_text.split()) / len(doc_pair.original_text.split()) if doc_pair.original_text.split() else 0,
                }
                
                edited_metadata = {
                    'word_count': len(doc_pair.edited_text.split()),
                    'character_count': len(doc_pair.edited_text),
                    'sentence_count': len([s for s in doc_pair.edited_text.split('.') if s.strip()]),
                    'avg_word_length': sum(len(w) for w in doc_pair.edited_text.split()) / len(doc_pair.edited_text.split()) if doc_pair.edited_text.split() else 0,
                }
                
                # Create exporter
                export_data = ExportFactory.export(
                    format_type=selected_format,
                    analysis_result=result,
                    doc_pair=doc_pair,
                    original_metadata=orig_metadata,
                    edited_metadata=edited_metadata,
                    include_original_text=include_original,
                    include_edited_text=include_edited,
                    include_metrics=include_metrics,
                    include_ai_isms=include_ai_isms,
                    include_charts=include_charts,
                    include_benchmarks=include_benchmarks,
                    calibration=calibration_payload,
                )
                
                # Prepare download - handle both string and binary data
                if isinstance(export_data, bytes):
                    download_data = export_data
                elif isinstance(export_data, io.BytesIO):
                    download_data = export_data.getvalue()
                else:
                    download_data = export_data
                
                if selected_format == "csv":
                    st.success("✓ CSV generated successfully!")
                    st.download_button(
                        label="📥 Download CSV",
                        data=download_data if isinstance(download_data, str) else download_data.decode('utf-8') if isinstance(download_data, bytes) else str(download_data),
                        file_name=f"voicetracer_analysis_{result.doc_pair_id[:8]}.csv",
                        mime="text/csv"
                    )
                
                elif selected_format == "json":
                    st.success("✓ JSON generated successfully!")
                    st.download_button(
                        label="📥 Download JSON",
                        data=download_data if isinstance(download_data, str) else download_data.decode('utf-8') if isinstance(download_data, bytes) else str(download_data),
                        file_name=f"voicetracer_analysis_{result.doc_pair_id[:8]}.json",
                        mime="application/json"
                    )
                
                elif selected_format in ["docx", "xlsx", "pdf"]:
                    st.success(f"✓ {selected_format.upper()} generated successfully!")
                    
                    mime_types = {
                        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "pdf": "application/pdf",
                    }
                    
                    st.download_button(
                        label=f"📥 Download {selected_format.upper()}",
                        data=download_data,
                        file_name=f"voicetracer_analysis_{result.doc_pair_id[:8]}.{selected_format}",
                        mime=mime_types[selected_format]
                    )
                
                # Show preview for text formats
                if selected_format in ["csv", "json"]:
                    with st.expander("📋 Preview"):
                        preview_str = download_data if isinstance(download_data, str) else download_data.decode('utf-8') if isinstance(download_data, bytes) else str(download_data)
                        if selected_format == "csv":
                            st.text(preview_str[:500] + "..." if len(preview_str) > 500 else preview_str)
                        else:
                            import json as json_lib
                            data = json_lib.loads(preview_str)
                            st.json(data)
                
                # Additional information
                st.markdown("---")
                st.markdown("### What's Included")
                
                include_cols = []
                if include_original:
                    include_cols.append("Original Text")
                if include_edited:
                    include_cols.append("Edited Text")
                if include_metrics:
                    include_cols.append("Metrics Data")
                if include_ai_isms:
                    include_cols.append("AI-ism Phrases")
                if include_benchmarks:
                    include_cols.append("Benchmark Comparisons")
                
                st.info(f"✓ Included: {', '.join(include_cols)}")
            
            except Exception as e:
                st.error(f"Error generating export: {str(e)}")
                st.info("Please ensure all required data is available and try again.")
    
    st.markdown("---")
    st.markdown("### About Exports")
    with st.expander("Format Guide"):
        st.markdown("""
        **CSV**: Best for data analysis in Excel, R, or Python. Includes all metrics in tabular format.
        
        **JSON**: Best for programmatic access and integration with other tools. Structured and machine-readable.
        
        **Word (DOCX)**: Best for editing and sharing. Includes formatted text with your analysis.
        
        **Excel (XLSX)**: Best for further analysis with charts and formulas. Multiple sheets with organized data.
        
        **PDF**: Best for sharing and archiving. Professional formatted document ready for publication.
        """)

    st.markdown("---")
    _render_next_step_button(4, is_ready=True)


# ============================================================================
# MAIN APP FLOW
# ============================================================================
def main():
    """Main application flow."""
    # Initialize session state
    if 'nav_step' not in st.session_state:
        st.session_state.nav_step = 1

    pending_step = st.session_state.pop("pending_nav_step", None)
    if pending_step is not None:
        st.session_state.nav_step = pending_step
    
    # Setup sidebar
    current_step = setup_sidebar()

    st.warning(
        "This app is not a commercial AI detection tool. It doesn't guarantee 100% accuracy. "
        "It is bulit for research purpose. A primary focus of this research is the potential "
        "bias against L2 (non-native English) learners, whose formal and highly structured writing "
        "styles are often misidentified as AI-generated. Visitors are cautioned that this tool may "
        "flag human text as \"AI-like\" if the writer employs high levels of academic vocabulary or "
        "repetitive syntactic patterns common in formal L2 prose. This analyzer is intended for "
        "academic inquiry into the \"homogenization of voice\" by AI and should not be used as a "
        "substitute for professional, commercial detection services."
    )
    
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
