# VoiceTracer Developer & Deployment Guide

## Project Overview

**Project**: VoiceTracer  
**Purpose**: Measure and document stylistic homogenization in L2 academic writing when using AI editing tools  
**Type**: Streamlit web application (Python)  
**Status**: Phase 9 - Ready for deployment  
**License**: Open source (MIT proposed)

---

## Architecture Overview

```
VoiceTracer/
├── src/
│   ├── app.py                    # Main Streamlit application
│   ├── models.py                 # Data models & structures
│   ├── metrics_spec.py           # Metric definitions & formulas
│   ├── text_processor.py         # Text analysis & preprocessing
│   ├── metric_calculator.py      # Metric calculation engine
│   ├── visualizations.py         # Chart & visualization generation
│   ├── exporters.py              # Export to PDF/DOCX/XLSX/JSON/CSV
│   └── persistence.py            # Session management & auto-save
├── tests/
│   └── test_voicetracer.py      # Unit & integration tests
├── docs/
│   ├── USER_GUIDE.md            # End-user documentation
│   └── DEVELOPER_GUIDE.md        # This file
├── pyproject.toml               # Project metadata & dependencies
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── REQUIREMENTS.md              # Project requirements & specs
└── README.md                    # Quick start guide
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Streamlit | ≥1.28.0 | Web UI & state management |
| **NLP** | Rule-based | n/a | Lightweight text parsing & heuristics |
| **Data** | pandas | ≥2.0.0 | Data manipulation & analysis |
| **Visualization** | Plotly | ≥5.18.0 | Interactive charts |
| **Export - PDF** | reportlab | ≥4.0.0 | PDF generation |
| **Export - Office** | python-docx, openpyxl, python-pptx | Latest | Office format export |
| **Export - PDF (read)** | PyPDF2 | ≥3.16.0 | PDF file handling |
| **Database** | SQLite3 | Built-in | Session persistence |
| **Testing** | pytest | ≥7.4.0 | Unit & integration tests |

---

## Environment Setup

### Prerequisites
- Python 3.9+
- pip or conda
- Git (for version control)

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/VoiceTracer/VoiceTracer.git
cd VoiceTracer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"  # Installs project + dev dependencies

# Run tests
pytest tests/ -v

# Run Streamlit app locally
streamlit run src/app.py
```

### Environment Variables (Optional)
```bash
# .env file (for future use)
VOICETRACER_DEBUG=true
VOICETRACER_MAX_TEXT_LENGTH=50000
VOICETRACER_DB_PATH=.voicetracer/sessions.db
```

---

## Development Workflow

### Code Structure

#### 1. **models.py** — Data Models
Contains Pydantic-like dataclasses for:
- `DocumentPair` — Original + edited text pair
- `TextMetadata` — Text statistics
- `MetricScores` — Individual metric values (0-1 normalized)
- `MetricDeltas` — Changes between original & edited
- `AnalysisResult` — Complete analysis output
- `Session` — User session tracking
- `Benchmark` — Comparison baselines

#### 2. **metrics_spec.py** — Metric Specifications
Defines each metric with:
- Mathematical formula
- Calculation method
- Interpretation guides
- AI-ism phrase database
- Normalization rules

**Key metrics:**
- **Burstiness**: SD(sentence_lengths) / mean(sentence_lengths)
- **Lexical Diversity**: MTLD-normalized to 0-1
- **Syntactic Complexity**: Composite (ASL, subordination, modifiers)
- **AI-ism Likelihood**: Phrase + pattern detection (0-100)
- **Function Word Ratio**: Function words / total words
- **Discourse Marker Density**: Markers per 1,000 words
- **Information Density**: Content ratio + unique content + proper noun signals
- **Epistemic Hedging**: Hedging markers per word

#### 3. **text_processor.py** — Text Analysis
Provides utilities for:
- Sentence/token extraction
- Word filtering (no punctuation)
- N-gram extraction
- Clause detection
- Passive voice estimation
- `TextAnalysisPreprocessor` — All-in-one pipeline

#### 4. **metric_calculator.py** — Metric Engine
Individual calculators:
- `BurstinessCalculator` — Sentence length variation
- `LexicalDiversityCalculator` — Vocabulary richness
- `SyntacticComplexityCalculator` — Structure sophistication
- `AIismCalculator` — Formulaic pattern detection
- `FunctionWordRatioCalculator` — Grammatical scaffolding ratio
- `DiscourseMarkerDensityCalculator` — Connector density
- `InformationDensityCalculator` — Content specificity
- `EpistemicHedgingCalculator` — Uncertainty markers

Main engine:
- `MetricCalculationEngine` — Calculates all metrics from text
- `MetricComparisonEngine` — Compares original vs. edited

#### 5. **visualizations.py** — Charts & Visuals
Plotly-based chart generators:
- `RadarChartGenerator` — 8-axis comparison
- `BarChartGenerator` — Side-by-side metrics
- `DeltaVisualization` — Percent change charts
- `TextDiffVisualizer` — Side-by-side text diff
- `MetricsOverTimeChart` — Time-series (if multiple analyses)

#### 6. **exporters.py** — Export Formats
Format-specific exporters:
- `CSVExporter` — Tabular data for analysis
- `JSONExporter` — Full structured export
- `ExcelExporter` — Multi-sheet workbook
- `PDFExporter` — Professional PDF report
- `DocxExporter` — Editable Word document
- `PowerPointExporter` — Presentation slides
- `ExportFactory` — Unified interface

#### 7. **persistence.py** — Session Management
- `SessionDatabase` — SQLite-based persistence
- `AutoSaveManager` — 30-second auto-save
- `SessionRecovery` — Restore state on reload
- `DataStorage` — Import/export utilities

#### 8. **app.py** — Streamlit UI
4-step dashboard:
- **Step 1**: Text input (paste, upload, samples)
- **Step 2**: Metrics display with explanations
- **Step 3**: Visualizations (charts, diff)
- **Step 4**: Export options & formats

Sidebar navigation, session management, help system.

---

## Key Algorithms

### Burstiness Calculation
```python
# Pseudocode
mean_length = average(sentence_word_counts)
std_dev = standard_deviation(sentence_word_counts)
burstiness = std_dev / mean_length
```

**Interpretation:**
- < 0.8: Machine-like (AI-edited)
- > 1.5: Human-like (authentic)

### Lexical Diversity (MTLD)
```python
# Segmented type-token ratio
# Threshold = 0.72
# Divide text into segments where TTR ≤ threshold
# Average TTR across segments, multiply by text_length
```

**Result:** Typically 70-150, normalized to 0-1

### Syntactic Complexity
```python
# Composite score
ASL = average_sentence_length / 30  # Normalize
SUB = subordination_ratio  # 0-1 naturally
MOD = modifier_density  # 0-1 naturally

complexity = (ASL × 0.4) + (SUB × 0.3) + (MOD × 0.3)
```

### AI-ism Detection
```python
# Keyword matching + frequency scoring
scores = {
    'openings': count_opening_hedges() * weight,
    'closings': count_closing_phrases() * weight,
    'connectors': count_formulaic_connectors() * weight,
    'patterns': detect_repetitive_patterns() * weight,
}
ai_ism_score = sum(scores) / max_possible * 100  # 0-100
```

---

## Testing Strategy

### Unit Tests (`tests/test_voicetracer.py`)

1. **Text Processing**
   - Sentence extraction accuracy
   - Tokenization correctness
   - N-gram generation

2. **Metrics Calculation**
   - Burstiness (human-like vs. machine-like)
   - Lexical diversity ranges
   - Syntactic complexity ordering
   - AI-ism detection

3. **Metric Validation (Parity Check)**
   - Metrics stay within expected ranges
   - Sample texts produce consistent results
   - Changes are directionally correct

4. **Exports**
   - CSV format validity
   - JSON structure correctness
   - Excel workbook creation

5. **Accessibility**
   - Color contrast ratios (WCAG AA)
   - Heading hierarchy

### Running Tests
```bash
pytest tests/ -v                    # All tests
pytest tests/test_voicetracer.py::TestMetricCalculators -v  # Specific test class
pytest tests/ --cov=src            # With coverage report
```

### Validation Targets
- Metric accuracy: ±2% parity with manual calculation
- Export integrity: All files generated without errors
- Performance: Page load < 3s, metric calc < 2s for texts up to 5000 words
- Accessibility: WCAG 2.1 AA compliance

---

## Deployment Guide

### Option 1: Streamlit Cloud (Recommended for Prototype)

**Steps:**

1. **Create GitHub repository**
   ```bash
   git init
   git add .
   git commit -m "Initial VoiceTracer commit"
   git remote add origin https://github.com/YOUR-USERNAME/VoiceTracer.git
   git push -u origin main
   ```

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
   - Sign up with GitHub account
   - Click "New app"
   - Select your repository & `src/app.py`
   - Deploy

3. **Configure (in Streamlit Cloud settings)**
   ```toml
   [server]
   maxUploadSize = 50  # MB
   ```

4. **App will be live at:** `https://voicetracer.streamlit.app`

**Advantages:**
- Free hosting
- Automatic deployment on git push
- Built-in SSL/HTTPS
- No server management

**Limitations:**
- Community tier has rate limits
- SQLite database (not distributed across instances)
- 1GB max RAM for app

### Option 2: Docker (Production)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", "--server.port=8501"]
```

**Build & run:**
```bash
docker build -t voicetracer:latest .
docker run -p 8501:8501 voicetracer:latest
```

### Option 3: Traditional Server (AWS, Azure, etc.)

1. **Install on server**
   ```bash
   sudo apt update && sudo apt install python3.11 python3.11-venv
   git clone https://github.com/YOUR-USERNAME/VoiceTracer.git
   cd VoiceTracer
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -e .
   python -m spacy download en_core_web_sm
   ```

2. **Run with systemd service**
   ```ini
   [Unit]
   Description=VoiceTracer Streamlit App
   After=network.target
   
   [Service]
   Type=simple
   User=voicetracer
   WorkingDirectory=/home/voicetracer/VoiceTracer
   ExecStart=/home/voicetracer/VoiceTracer/venv/bin/streamlit run src/app.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Configure reverse proxy (nginx)**
   ```nginx
   server {
       listen 80;
       server_name voicetracer.example.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
       }
   }
   ```

---

## Database Schema

### SQLite Tables

```sql
-- Sessions
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    last_activity TIMESTAMP,
    data JSON
);

-- Document pairs
CREATE TABLE document_pairs (
    doc_pair_id TEXT PRIMARY KEY,
    session_id TEXT,
    original_text TEXT,
    edited_text TEXT,
    created_at TIMESTAMP
);

-- Analysis results
CREATE TABLE analysis_results (
    result_id TEXT PRIMARY KEY,
    doc_pair_id TEXT,
    session_id TEXT,
    metrics_json JSON,
    created_at TIMESTAMP
);

-- Recovery snapshots
CREATE TABLE recovery_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    session_id TEXT,
    snapshot_data JSON,
    created_at TIMESTAMP
);
```

---

## Contributing

### Code Style
- Follow PEP 8
- Use type hints
- docstrings for all functions
- Keep functions focused & testable

### Adding a New Metric

1. **Define in `metrics_spec.py`:**
   ```python
   MY_METRIC_DEFINITION = MetricDefinition(
       metric_type=MetricType.NEW_METRIC,
       name="My Metric",
       formula="formula here",
       # ... other fields
   )
   ```

2. **Implement calculator in `metric_calculator.py`:**
   ```python
   class MyMetricCalculator:
       @staticmethod
       def calculate(features: Dict) -> float:
           # Implementation
           return value
   ```

3. **Add to `MetricCalculationEngine.calculate_all_metrics()`**

4. **Add tests in `tests/test_voicetracer.py`**

5. **Update UI in `src/app.py`** (Step 2 metrics tabs)

---

## Known Limitations & Future Work

### Current Limitations (v0.1)
- ⚠️ NLP tools are English-only (no multilingual support yet)
- ⚠️ Max text size: 5000 words (to keep analysis fast)
- ⚠️ Export formats not fully implemented (PDF, DOCX, PPTX are placeholder)
- ⚠️ No user authentication (anonymized sessions only)
- ⚠️ SQLite not suitable for multi-instance deployment

### Future Enhancements
- [ ] Full export implementation (PDF with charts, DOCX with track changes)
- [ ] Support for multiple languages
- [ ] User accounts & saved analyses
- [ ] Instructor dashboard for bulk analysis
- [ ] API endpoint for integration
- [ ] Custom metric configuration
- [ ] Batch analysis
- [ ] Mobile app

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'spacy'"
```bash
pip install -e .
python -m spacy download en_core_web_sm
```

### "Streamlit port 8501 already in use"
```bash
streamlit run src/app.py --server.port 8502
```

### "Metrics seem off for very short texts"
Text must be at least 2 sentences. Metrics are normalized for texts 100+ words.

### "App is slow for large texts"
Processing is O(n) for text length. Texts >5000 words may take 2-3 seconds.
Consider warning users or implementing text truncation.

---

## Performance Metrics

| Operation | Typical Time |
|-----------|------------|
| Load page | 0.5-1s |
| Parse text (1000 words) | 0.3s |
| Calculate all 4 metrics | 0.5-1s |
| Generate visualizations | 0.2s |
| Export to CSV | 0.1s |
| Export to Excel | 0.5s |
| **Total for full analysis** | **2-3 seconds** |

---

## Security Considerations

- **Text handling**: Texts stored in-memory by default, optionally in SQLite
- **No external API calls**: All processing local
- **No tracking**: No analytics or usage tracking
- **Open source**: Code is auditable
- **WCAG A11y**: Accessible UI for all users

---

## License & Attribution

Proposed: MIT License

**Attribution required:**
- VoiceTracer (2026)
- Supports thesis: "The Monolingualism of the Machine"
- Developed for L2 writing research

---

## Roadmap

### Phase 10+ (Future)
1. **v0.2**: Full export implementation
2. **v0.3**: User authentication & accounts
3. **v0.4**: Instructor dashboard
4. **v1.0**: Production release with API
5. **v1.1+**: Multilingual support, advanced features

---

## Contact & Support

- **GitHub Issues**: https://github.com/VoiceTracer/issues
- **Thesis Research**: Supported by [Your University]
- **Questions**: [Your Email]

---

**Last Updated**: February 4, 2026  
**Project Status**: Phase 9 - Ready for Deployment
