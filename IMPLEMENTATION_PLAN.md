# 🚀 VoiceTracer Core 8 Metrics - Implementation Plan

**Goal**: Expand from 4 metrics to 8 metrics for 70-90% AI detection accuracy  
**Timeline**: 6-8 hours development + 2-3 hours UI/testing  
**Deployment**: Streamlit-ready, lightweight, no LLMs

---

## 📋 Current State Assessment

### ✅ Already Implemented (4 metrics)
1. **Burstiness** - Sentence variance calculation
2. **Lexical Diversity** - MTLD calculation  
3. **Syntactic Complexity** - Dependency tree depth
4. **AI-ism Detection** - Phrasal pattern matching

### 🆕 To Be Implemented (4 metrics)
5. **Function Word Ratio** - POS-based grammatical scaffolding
6. **Discourse Marker Density** - Logical connector frequency
7. **Information Density** - Content vs. filler ratio
8. **Epistemic Hedging Index** - Confidence vs. uncertainty markers

---

## 🎯 Implementation Phases

---

## **PHASE 1: Foundation Setup** ⏱️ 30 minutes

### Tasks
- [ ] Create lexicon files for new metrics
- [ ] Update data models to support 8 metrics
- [ ] Prepare test data for validation

### Deliverables

#### 1.1 Create Lexicon Directory
```
src/lexicons/
├── discourse_markers.py
├── epistemic_hedging.py
└── function_words.py
```

#### 1.2 Update MetricScores Model
File: `src/models.py`
```python
@dataclass
class MetricScores:
    # Existing
    burstiness: float
    lexical_diversity: float
    syntactic_complexity: float
    ai_ism_likelihood: float
    
    # New additions
    function_word_ratio: float = 0.0
    discourse_marker_density: float = 0.0
    information_density: float = 0.0
    epistemic_hedging_index: float = 0.0
```

#### 1.3 Update MetricDeltas Model
File: `src/models.py`
```python
@dataclass
class MetricDeltas:
    # Existing deltas...
    
    # New deltas
    function_word_ratio_delta: float = 0.0
    function_word_ratio_pct_change: float = 0.0
    discourse_marker_density_delta: float = 0.0
    discourse_marker_density_pct_change: float = 0.0
    information_density_delta: float = 0.0
    information_density_pct_change: float = 0.0
    epistemic_hedging_index_delta: float = 0.0
    epistemic_hedging_index_pct_change: float = 0.0
```

### Validation
- [ ] Models update without breaking existing code
- [ ] Test suite still passes (20/20 tests)

---

## **PHASE 2: Metric Implementation** ⏱️ 4-5 hours

### **2.1 Function Word Ratio** ⏱️ 1 hour

#### Algorithm
```python
def calculate_function_word_ratio(doc):
    """
    Calculate proportion of grammatical function words.
    
    Function words: articles, prepositions, pronouns, 
                   auxiliaries, conjunctions, determiners
    
    AI signature: 55-65% (high)
    Human range: 45-55% (moderate)
    """
    function_pos_tags = {'DET', 'ADP', 'CCONJ', 'SCONJ', 
                        'AUX', 'PRON', 'PART'}
    
    function_count = sum(1 for token in doc 
                        if token.pos_ in function_pos_tags)
    total_tokens = len([t for t in doc if not t.is_punct])
    
    ratio = function_count / total_tokens if total_tokens > 0 else 0
    
    # Normalize: higher ratio = more AI-like
    normalized = min((ratio - 0.45) / 0.20, 1.0) if ratio > 0.45 else 0.0
    
    return {
        'raw_ratio': ratio,
        'normalized_score': max(0, min(normalized, 1.0)),
        'function_count': function_count,
        'total_tokens': total_tokens
    }
```

#### Implementation Location
- File: `src/metric_calculator.py`
- Add method to `MetricCalculator` class
- Integration point: Call from `calculate_all_metrics()`

#### Test Case
```python
def test_function_word_ratio():
    # AI-like text (high function words)
    ai_text = "The analysis is in the report that was on the desk."
    # Human-like text (lower function words)
    human_text = "Scientists discovered remarkable fossils yesterday."
    
    assert fwr_ai > 0.6
    assert fwr_human < 0.5
```

---

### **2.2 Discourse Marker Density** ⏱️ 1 hour

#### Algorithm
```python
def calculate_discourse_marker_density(text, doc):
    """
    Calculate frequency of explicit logical connectors.
    
    AI signature: 15-30 per 1000 words (overuses)
    Human range: 5-15 per 1000 words (sparse)
    """
    discourse_markers = {
        'however', 'moreover', 'furthermore', 'therefore',
        'consequently', 'thus', 'hence', 'indeed',
        'in addition', 'on the other hand', 'as a result',
        'for instance', 'in conclusion', 'additionally',
        'meanwhile', 'subsequently', 'nevertheless',
        'in contrast', 'similarly', 'specifically'
    }
    
    text_lower = text.lower()
    marker_count = sum(text_lower.count(marker) 
                      for marker in discourse_markers)
    
    word_count = len([t for t in doc if not t.is_punct and not t.is_space])
    
    # Per 1000 words
    density = (marker_count / word_count) * 1000 if word_count > 0 else 0
    
    # Normalize: higher density = more AI-like
    normalized = min(density / 30, 1.0)
    
    return {
        'density_per_1000': density,
        'normalized_score': normalized,
        'marker_count': marker_count,
        'word_count': word_count
    }
```

#### Lexicon File
Create: `src/lexicons/discourse_markers.py`
```python
DISCOURSE_MARKERS = {
    'transition': ['however', 'moreover', 'furthermore', 'nevertheless'],
    'causal': ['therefore', 'thus', 'consequently', 'hence'],
    'additive': ['additionally', 'in addition', 'besides', 'also'],
    'illustrative': ['for example', 'for instance', 'specifically'],
    'conclusive': ['in conclusion', 'in summary', 'to sum up'],
    'contrastive': ['in contrast', 'on the other hand', 'conversely']
}

def get_all_markers():
    markers = set()
    for category in DISCOURSE_MARKERS.values():
        markers.update(category)
    return markers
```

#### Test Case
```python
def test_discourse_marker_density():
    ai_text = "Moreover, this is important. Furthermore, it matters. However, we must consider. Therefore, conclude."
    human_text = "This matters. We should think about it. The conclusion is clear."
    
    assert dmd_ai > 20  # High density
    assert dmd_human < 10  # Low density
```

---

### **2.3 Information Density** ⏱️ 1.5 hours

#### Algorithm
```python
def calculate_information_density(doc):
    """
    Calculate content vs. filler ratio using NER + POS.
    
    Components:
    1. Named Entity Density (specificity)
    2. Content Word Ratio (noun/verb/adj/adv)
    3. Unique Content Words (vocabulary richness)
    
    AI signature: 0.25-0.45 (verbose, low info)
    Human range: 0.50-0.70 (concise, high info)
    """
    # 1. Named Entity Density
    entities = [ent for ent in doc.ents]
    tokens = [t for t in doc if not t.is_punct and not t.is_space]
    ner_density = (len(entities) / len(tokens)) * 100 if tokens else 0
    
    # 2. Content Word Ratio
    content_pos = {'NOUN', 'VERB', 'ADJ', 'ADV'}
    content_words = [t for t in tokens if t.pos_ in content_pos]
    content_ratio = len(content_words) / len(tokens) if tokens else 0
    
    # 3. Unique Content Word Ratio
    unique_content = set(t.lemma_.lower() for t in content_words 
                        if t.lemma_.isalpha())
    unique_ratio = (len(unique_content) / len(content_words) 
                   if content_words else 0)
    
    # Composite Information Density
    # Higher = more informative = more human
    info_density = (
        min(ner_density / 50, 1.0) * 0.3 +
        content_ratio * 0.4 +
        unique_ratio * 0.3
    )
    
    # Invert for AI detection (low density = AI-like)
    normalized = 1.0 - min(info_density / 0.70, 1.0)
    
    return {
        'composite_score': info_density,
        'normalized_score': normalized,
        'ner_density': ner_density,
        'content_ratio': content_ratio,
        'unique_content_ratio': unique_ratio,
        'entity_count': len(entities),
        'content_word_count': len(content_words)
    }
```

#### Test Case
```python
def test_information_density():
    # AI text - verbose, low info
    ai_text = "It is important to note that the system has the ability to..."
    
    # Human text - specific, high info
    human_text = "Dr. Chen discovered novel CRISPR variants in Madagascar bacteria."
    
    assert id_ai < 0.4  # Low density
    assert id_human > 0.6  # High density
```

---

### **2.4 Epistemic Hedging Index** ⏱️ 1 hour

#### Algorithm
```python
def calculate_epistemic_hedging_index(text):
    """
    Calculate uncertainty markers vs. confidence markers.
    
    AI signature: 0.02-0.08 (overconfident)
    Human range: 0.08-0.15 (appropriately hedged)
    """
    epistemic_hedges = {
        'perhaps', 'possibly', 'might', 'may', 'could',
        'arguably', 'seemingly', 'apparently', 'tends to',
        'appears to', 'suggests', 'indicates', 'likely',
        'probably', 'I think', 'I believe', 'in my view',
        'it seems', 'one could argue', 'to some extent'
    }
    
    confidence_markers = {
        'certainly', 'definitely', 'absolutely', 'obviously',
        'clearly', 'undoubtedly', 'without doubt', 'must be',
        'is certain', 'proves', 'demonstrates conclusively'
    }
    
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    hedge_count = sum(text_lower.count(hedge) for hedge in epistemic_hedges)
    confidence_count = sum(text_lower.count(marker) 
                          for marker in confidence_markers)
    
    # Hedging frequency (per 1000 words)
    hedge_frequency = (hedge_count / word_count) * 1000 if word_count > 0 else 0
    
    # Penalty for overconfidence
    confidence_penalty = confidence_count - hedge_count
    adjusted_hedging = hedge_frequency - (confidence_penalty * 2)
    
    # Normalize: low hedging = AI-like
    normalized = 1.0 - min(max(adjusted_hedging, 0) / 150, 1.0)
    
    return {
        'hedge_frequency': hedge_frequency,
        'normalized_score': normalized,
        'hedge_count': hedge_count,
        'confidence_count': confidence_count,
        'confidence_penalty': confidence_penalty,
        'word_count': word_count
    }
```

#### Lexicon File
Create: `src/lexicons/epistemic_hedging.py`
```python
EPISTEMIC_HEDGES = {
    'modal_verbs': ['might', 'may', 'could', 'would'],
    'adverbs': ['perhaps', 'possibly', 'probably', 'likely'],
    'phrases': ['it seems', 'appears to', 'tends to', 'suggests that'],
    'stance_markers': ['I think', 'I believe', 'in my view', 'arguably']
}

CONFIDENCE_MARKERS = {
    'certainty': ['certainly', 'definitely', 'absolutely'],
    'evidence': ['clearly', 'obviously', 'evidently'],
    'strong_claims': ['must be', 'proves', 'demonstrates']
}
```

#### Test Case
```python
def test_epistemic_hedging():
    # AI - overconfident
    ai_text = "This clearly demonstrates that the system is absolutely perfect."
    
    # Human - hedged
    human_text = "This suggests that the approach might be effective, though further research is needed."
    
    assert ehi_ai < 0.05  # Low hedging
    assert ehi_human > 0.10  # Appropriate hedging
```

---

## **PHASE 3: Integration** ⏱️ 1.5 hours

### 3.1 Update MetricCalculator Class
File: `src/metric_calculator.py`

```python
class MetricCalculator:
    def calculate_all_metrics(self, original_text, edited_text):
        # Process both texts
        original_doc = self.nlp(original_text)
        edited_doc = self.nlp(edited_text)
        
        # Existing metrics (1-4)
        original_burstiness = self.calculate_burstiness(original_doc)
        original_lexical = self.calculate_lexical_diversity(original_doc)
        original_syntactic = self.calculate_syntactic_complexity(original_doc)
        original_ai_ism = self.calculate_ai_ism_likelihood(original_text, original_doc)
        
        # NEW: Add metrics 5-8
        original_fwr = self.calculate_function_word_ratio(original_doc)
        original_dmd = self.calculate_discourse_marker_density(original_text, original_doc)
        original_id = self.calculate_information_density(original_doc)
        original_ehi = self.calculate_epistemic_hedging_index(original_text)
        
        # Repeat for edited text...
        
        # Create MetricScores objects with all 8 metrics
        original_metrics = MetricScores(
            burstiness=original_burstiness['normalized_score'],
            lexical_diversity=original_lexical['normalized_score'],
            syntactic_complexity=original_syntactic['normalized_score'],
            ai_ism_likelihood=original_ai_ism['normalized_score'],
            function_word_ratio=original_fwr['normalized_score'],
            discourse_marker_density=original_dmd['normalized_score'],
            information_density=original_id['normalized_score'],
            epistemic_hedging_index=original_ehi['normalized_score']
        )
        
        # Calculate deltas for all 8 metrics
        # ...
```

### 3.2 Update Metric Specifications
File: `src/metrics_spec.py`

Add specifications for the 4 new metrics including:
- Name, description
- Formula
- Interpretation scale
- Thresholds (human vs. AI ranges)
- Research citations

---

## **PHASE 4: UI Updates** ⏱️ 2 hours

### 4.1 Update Dashboard Metrics Display
File: `src/app.py`

#### Metric Cards (expand from 4 to 8)
```python
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

# Existing metrics in col1-col4
# New metrics in col5-col8

with col5:
    display_metric_card(
        "Function Word Ratio",
        original_metrics.function_word_ratio,
        edited_metrics.function_word_ratio,
        "AI texts overuse grammatical scaffolding"
    )

# ... repeat for col6-col8
```

### 4.2 Update Visualizations
File: `src/visualizations.py`

#### Radar Chart (4 axes → 8 axes)
```python
def create_radar_chart(original_metrics, edited_metrics):
    categories = [
        'Burstiness',
        'Lexical Diversity',
        'Syntactic Complexity',
        'AI-ism Likelihood',
        'Function Words',      # NEW
        'Discourse Markers',   # NEW
        'Info Density',        # NEW
        'Hedging Index'        # NEW
    ]
    
    original_values = [
        original_metrics.burstiness,
        original_metrics.lexical_diversity,
        original_metrics.syntactic_complexity,
        original_metrics.ai_ism_likelihood,
        original_metrics.function_word_ratio,      # NEW
        original_metrics.discourse_marker_density, # NEW
        original_metrics.information_density,      # NEW
        original_metrics.epistemic_hedging_index   # NEW
    ]
    # ... create 8-axis radar chart
```

#### Bar Chart (expand to 8 bars)
Update comparison bar chart to show all 8 metrics side-by-side.

---

## **PHASE 5: Export Updates** ⏱️ 1 hour

### 5.1 Update CSV Exporter
File: `src/exporters.py`

```python
class CSVExporter:
    @staticmethod
    def export(result, doc_pair, original_metadata, edited_metadata):
        # ... existing code ...
        
        # Add 4 new metric rows
        writer.writerow(['', 'Function Word Ratio', 
                        f"{result.original_metrics.function_word_ratio:.3f}",
                        f"{result.edited_metrics.function_word_ratio:.3f}"])
        # ... repeat for other 3 metrics
```

### 5.2 Update JSON Exporter
Add new metrics to JSON structure.

### 5.3 Update Other Exporters
- PDF reports
- DOCX documents
- Excel spreadsheets

---

## **PHASE 6: Testing & Validation** ⏱️ 1.5 hours

### 6.1 Unit Tests
File: `tests/test_voicetracer.py`

```python
class TestNewMetrics:
    def test_function_word_ratio_range(self):
        """Test FWR produces valid 0-1 scores."""
        # ... test implementation
        
    def test_discourse_marker_density_detection(self):
        """Test DMD identifies overuse of connectors."""
        # ... test implementation
        
    def test_information_density_calculation(self):
        """Test ID distinguishes verbose vs. concise."""
        # ... test implementation
        
    def test_epistemic_hedging_confidence(self):
        """Test EHI detects hedging vs. overconfidence."""
        # ... test implementation
```

Add 8-10 new test cases covering:
- Individual metric calculations
- Edge cases (empty text, very short text)
- Integration with existing system
- Export format validation

### 6.2 Integration Testing
- [ ] Run full analysis with 8 metrics
- [ ] Verify all visualizations render correctly
- [ ] Test export formats contain all 8 metrics
- [ ] Validate persistence saves all data

### 6.3 Performance Testing
- [ ] Measure analysis time with 8 metrics
- [ ] Target: <2 seconds for 1000-word document
- [ ] Memory usage: <100MB for typical analysis

---

## **PHASE 7: Documentation** ⏱️ 1 hour

### 7.1 Update User Guide
File: `docs/USER_GUIDE.md`

Add sections explaining:
- What each new metric measures
- How to interpret scores
- Examples of human vs. AI patterns

### 7.2 Update Developer Guide
File: `docs/DEVELOPER_GUIDE.md`

Document:
- New metric calculation algorithms
- Lexicon files and how to update them
- Testing procedures for new metrics

### 7.3 Update README
File: `README.md`

Update feature list:
- From "4 core metrics" to "8 core metrics"
- Add brief descriptions of new metrics

---

## 📊 Success Criteria

### Functional Requirements
- ✅ All 8 metrics calculate correctly
- ✅ Results display in dashboard (4x2 grid)
- ✅ Radar chart shows 8 axes
- ✅ Exports include all metrics
- ✅ Test suite passes (target: 28/28 tests)

### Performance Requirements
- ✅ Analysis time: <2 seconds for 1000 words
- ✅ Memory usage: <100MB
- ✅ Streamlit app loads in <3 seconds

### Accuracy Requirements
- ✅ Target: 75-85% detection accuracy
- ✅ Validated on sample AI vs. human texts
- ✅ False positive rate <20%

---

## 🗓️ Timeline Summary

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 1. Foundation Setup | 30 min | 30 min |
| 2. Metric Implementation | 4.5 hours | 5 hours |
| 3. Integration | 1.5 hours | 6.5 hours |
| 4. UI Updates | 2 hours | 8.5 hours |
| 5. Export Updates | 1 hour | 9.5 hours |
| 6. Testing | 1.5 hours | 11 hours |
| 7. Documentation | 1 hour | 12 hours |

**Total Development Time: 12 hours** (1.5 work days)

**Realistic with breaks: 2 full work days**

---

## 🚦 Implementation Order (Recommended)

### Day 1 (6 hours)
1. ✅ Phase 1: Foundation Setup (30 min)
2. ✅ Phase 2.1: Function Word Ratio (1 hour)
3. ✅ Phase 2.2: Discourse Marker Density (1 hour)
4. ✅ Phase 2.3: Information Density (1.5 hours)
5. ✅ Phase 2.4: Epistemic Hedging (1 hour)
6. ✅ Phase 3: Integration (1 hour partial)

### Day 2 (6 hours)
1. ✅ Phase 3: Integration completion (30 min)
2. ✅ Phase 4: UI Updates (2 hours)
3. ✅ Phase 5: Export Updates (1 hour)
4. ✅ Phase 6: Testing (1.5 hours)
5. ✅ Phase 7: Documentation (1 hour)

---

## 🔧 Development Environment Setup

### Before Starting
```bash
# Ensure all dependencies installed
cd /workspaces/VoiceTracer
pip install -e .

# Verify spaCy model
python -m spacy download en_core_web_sm

# Run existing tests
pytest tests/test_voicetracer.py -v

# Verify app runs
streamlit run src/app.py
```

### During Development
- Keep Streamlit app running in background
- Test each metric immediately after implementation
- Commit after each phase completion
- Use descriptive commit messages

---

## 🎯 Next Steps

**Ready to begin?** 

Start with **Phase 1: Foundation Setup**
```bash
# Create lexicon directory
mkdir -p src/lexicons

# Begin implementation
# Start with discourse_markers.py lexicon file
```

Would you like me to:
1. ✅ **Start Phase 1 now** - Create foundation files
2. 📋 Provide detailed code for a specific metric first
3. 🔍 Review/adjust the plan before starting

---

## 📈 Expected Outcome

After completing all phases:

```
VoiceTracer v2.0
├─ 8 Core Metrics ✅
├─ 75-85% Detection Accuracy ✅
├─ <2s Analysis Time ✅
├─ Streamlit Deployment Ready ✅
├─ Comprehensive Test Suite ✅
└─ Complete Documentation ✅
```

**This system will be production-ready for your thesis research while remaining lightweight and deployable on Streamlit Cloud.**
