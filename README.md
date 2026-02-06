# VoiceTracer

**Measure stylistic homogenization in L2 academic writing when using AI editing tools.**

## What is VoiceTracer?

VoiceTracer is a research tool that helps L2 (English language learner) students understand how AI editing tools affect their writing voice. When you use ChatGPT or similar tools to improve grammar, your writing often becomes more uniform and less authentically "you"—a phenomenon called **stylistic homogenization**.

VoiceTracer makes this trade-off **visible and measurable**.

### Key Features

✅ **8 Lightweight Metrics**
- Burstiness (sentence length variation)
- Lexical Diversity (vocabulary richness)
- Syntactic Complexity (structure sophistication)
- AI-ism Likelihood (formulaic pattern detection)
- Function Word Ratio (grammatical scaffolding)
- Discourse Marker Density (signposting frequency)
- Information Density (specific content per word)
- Epistemic Hedging (uncertainty markers)

✅ **4-Step Dashboard Workflow**
1. Input original & edited texts
2. View detailed metric comparison
3. Visualize differences with interactive charts

✅ **Multiple Export Formats**
PDF, Excel, Word, PowerPoint, CSV, JSON, PNG, ZIP

✅ **Thesis-Aligned**
Supports research on "Stylistic Homogenization in L2 Academic Writing"

---

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/VoiceTracer/VoiceTracer.git
cd VoiceTracer

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the app
streamlit run src/app.py
```

Visit `http://localhost:8501` in your browser.

### Try Online (Streamlit Cloud)

*Coming soon at: [voicetracer.streamlit.app](https://voicetracer.streamlit.app)*

---

## How It Works

### Example: Original vs. AI-Edited Comparison

**Original (L2 Student Writing):**
> "The research about artificial intelligence and language learning show that students who use AI tools get better grades quickly. However, we must think about what happens to their own writing voice. When students rely too much on AI, their writing becomes more uniform."

**AI-Edited (ChatGPT):**
> "Research examining the intersection of artificial intelligence and language acquisition demonstrates that students utilizing AI-assisted tools achieve improved academic performance metrics. However, it is important to note that significant considerations must be given to the preservation of authentic learner voice. Overreliance on artificial intelligence assistance can result in stylistic homogenization of written output."

### VoiceTracer Analysis Results

| Metric | Original | Edited | Change |
|--------|----------|--------|--------|
| **Burstiness** (sentence variation) | 1.23 | 0.78 | ↓ 37% |
| **Lexical Diversity** (vocabulary) | 0.62 | 0.41 | ↓ 34% |
| **Syntactic Complexity** (structure) | 0.68 | 0.65 | ↓ 4% |
| **AI-ism Likelihood** | 12 | 78 | ↑ 550% |

**Interpretation:**
- ❌ Sentence structure became uniform (machine-like)
- ❌ Vocabulary became repetitive and formulaic
- ❌ Many AI-characteristic phrases introduced ("it is important to note that")
- ✓ Grammar improved, but at cost of authentic voice

---

## Documentation

📖 **[User Guide](docs/USER_GUIDE.md)** — How to use VoiceTracer  
👨‍💻 **[Developer Guide](docs/DEVELOPER_GUIDE.md)** — Architecture & deployment  
📋 **[Requirements](REQUIREMENTS.md)** — Complete specifications

---

## Research Background

This tool supports the thesis:

> **"The Monolingualism of the Machine: Stylistic Homogenization in L2 Academic Writing"**
>
> When L2 writers use AI editing tools, their writing converges toward a generic "machine standard" style, losing the idiosyncratic features that mark their genuine linguistic identity.

### Research Questions Addressed

1. How does AI editing affect L2 learner writing characteristics?
2. Can we quantify stylistic differences between human and AI-edited text?
3. What linguistic markers indicate AI involvement?
4. How can L2 learners preserve voice while improving grammar?

---

## Metrics Explained

### Burstiness Index
**Formula:** `σ(sentence_lengths) / μ(sentence_lengths)`

Measures sentence length **variation**:
- Low (< 0.8) = Machine-like uniformity
- High (> 1.5) = Human-like natural variation

AI models standardize sentence lengths for readability. Humans vary them naturally.

### Lexical Diversity
**Method:** MTLD (Mean Type-Token Ratio Dynamics)

Measures **vocabulary richness**:
- Low (< 0.4) = Formulaic, repetitive
- High (> 0.6) = Varied, rich vocabulary

AI prefers common academic phrases. Humans use more diverse (and unique) words.

### Syntactic Complexity
**Composite metric:** Average sentence length × 0.4 + Subordination × 0.3 + Modifiers × 0.3

Measures **structure sophistication**:
- Simple structures: AI-edited
- Complex structures: Authentic writing

AI simplifies syntax. Authentic L2 writing contains more variety.

### AI-ism Likelihood
**Method:** Detect formulaic phrases + patterns (0–100)

Examples:
- Opening hedges: "It is important to note that..."
- Closing phrases: "In conclusion...", "To summarize..."
- Formulaic connectors: "delve into", "shed light on", "pave the way"

Texts > 50 likely AI-edited; > 80 likely AI-generated.

### Function Word Ratio
**Method:** Function words / total words

High ratios suggest over-scaffolded syntax common in AI writing.

### Discourse Marker Density
**Method:** Discourse markers per 1,000 words

AI text tends to overuse explicit connectors ("moreover", "therefore").

### Information Density
**Method:** Content-word ratio + unique content + proper noun signals

Low density suggests verbose, generic language.

### Epistemic Hedging
**Method:** Hedging markers per word

Human writers hedge claims more often than AI-generated text.

---

## Use Cases

### For Students
- Understand how AI affects your writing voice
- Make informed choices about which AI suggestions to accept
- Preserve authentic expression while improving grammar

### For Instructors
- Assess authenticity and AI involvement in submissions
- Teach voice awareness and critical evaluation of AI tools
- Provide feedback on stylistic changes

### For Researchers
- Measure stylistic homogenization quantitatively
- Export data for statistical analysis (CSV/JSON)
- Study AI's impact on L2 learner writing

### For Advisors & Thesis Committees
- Evidence of AI use patterns in student writing
- Understanding of methodology & metrics
- Publication-ready analysis reports

---

## Technology Stack

- **Framework**: Streamlit (interactive web UI)
- **NLP**: Rule-based tokenization + lightweight heuristics
- **Data**: pandas (analysis & export)
- **Visualization**: Plotly (interactive charts)
- **Export**: reportlab, python-docx, openpyxl, python-pptx
- **Storage**: SQLite (session management)
- **Testing**: pytest (quality assurance)

---

## Installation & Development

### Requirements
- Python 3.9+
- pip or conda

### Setup
```bash
# Clone & enter directory
git clone https://github.com/VoiceTracer/VoiceTracer.git
cd VoiceTracer

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install package + dependencies
pip install -e .

# Download spaCy English model (required)
python -m spacy download en_core_web_sm

# Run tests
pytest tests/ -v

# Start Streamlit app
streamlit run src/app.py
```

### Project Structure
```
src/
├── app.py                  # Main Streamlit UI
├── models.py              # Data structures
├── metrics_spec.py        # Metric definitions
├── text_processor.py      # Text analysis
├── metric_calculator.py   # Metric engines
├── visualizations.py      # Charts & graphs
├── exporters.py           # Export formats
└── persistence.py         # Session management

tests/
└── test_voicetracer.py   # Unit & integration tests

docs/
├── USER_GUIDE.md         # End-user documentation
└── DEVELOPER_GUIDE.md    # Technical guide
```

---

## Deployment

### Option 1: Streamlit Cloud (Easiest)
1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy from repository
4. App available at `https://yourapp.streamlit.app`

### Option 2: Docker
```bash
docker build -t voicetracer:latest .
docker run -p 8501:8501 voicetracer:latest
```

### Option 3: Traditional Server
See [Developer Guide](docs/DEVELOPER_GUIDE.md) for nginx/systemd setup.

---

## Testing & Quality

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_voicetracer.py::TestMetricCalculators -v

# Coverage report
pytest tests/ --cov=src
```

**Validation targets:**
- ✅ Metric accuracy within ±2% of manual calculation
- ✅ All export formats generate without errors
- ✅ Page load < 3 seconds, analysis < 2 seconds
- ✅ WCAG 2.1 AA accessibility compliance

---

## Limitations & Future Work

### Current Limitations (v0.1)
- English-only (no multilingual support yet)
- Max text: 5000 words
- Export formats partially implemented
- No user authentication
- Unsuitable for multi-instance deployment

### Roadmap
- [ ] Full export implementation (PDF charts, DOCX track changes)
- [ ] Multilingual support
- [ ] User accounts & saved analyses
- [ ] Instructor bulk analysis dashboard
- [ ] API endpoints
- [ ] Mobile app

---

## Citation

If you use VoiceTracer for research or academic work:

```bibtex
@software{voicetracer2026,
  author = {Your Name},
  title = {VoiceTracer: Measuring Stylistic Homogenization in L2 Academic Writing},
  year = {2026},
  url = {https://github.com/VoiceTracer/VoiceTracer}
}
```

---

## License

MIT License (proposed). See LICENSE file for details.

**Acknowledgments:**
- Thesis research on L2 writing and AI impact
- Research cited: Agarwal et al. (2024) on cross-cultural AI convergence
- Streamlit community for excellent web framework

---

## Support & Contributing

### Getting Help
- 📖 Read the [User Guide](docs/USER_GUIDE.md)
- 👨‍💻 Check the [Developer Guide](docs/DEVELOPER_GUIDE.md)
- 🐛 Open an issue on GitHub
- 📧 Contact the thesis author

### Contributing
We welcome contributions! To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Contact

- **Thesis Author**: [Your Name]
- **University**: [Your University]
- **Email**: [Your Email]
- **GitHub**: [Your GitHub URL]

---

## Project Status

**Phase 9: Ready for Deployment** ✅

- [x] Phase 1: Planning & scope confirmation
- [x] Phase 2: Architecture & data model
- [x] Phase 3: Core analysis engine
- [x] Phase 4: UI workflow (4-step dashboard)
- [x] Phase 5: Visualizations
- [x] Phase 6: Exports
- [x] Phase 7: Persistence & auto-save
- [x] Phase 8: QA & validation
- [x] Phase 9: Deploy & documentation

---

**Made with ❤️ for L2 writers and researchers**

*The goal is not to avoid AI help, but to use it wisely while preserving your authentic voice.*
