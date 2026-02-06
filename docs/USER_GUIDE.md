# VoiceTracer User Guide

## What is VoiceTracer?

VoiceTracer is a research tool designed to help L2 (English language learner) students understand how AI editing tools affect their writing voice. It measures **stylistic homogenization**—the process where AI-edited writing becomes more uniform and less authentically "you."

### Research Background

This tool supports the thesis: *"The Monolingualism of the Machine: Stylistic Homogenization in L2 Academic Writing"*

When L2 writers use AI tools like ChatGPT to improve grammar, they often trade their authentic voice for grammatical correctness. VoiceTracer makes this trade-off visible.

---

## How It Works: 4-Step Workflow

### Step 1: Input Your Texts
- Paste or upload your **original** (unassisted) writing
- Paste or upload your **AI-edited** version
- VoiceTracer accepts TXT, DOCX, and PDF files

### Step 2: View Your Metrics
VoiceTracer analyzes both texts and compares them across 8 core metrics:

1. **Burstiness** — How much your sentence lengths vary
   - ↑ High = Natural, human-like variation
   - ↓ Low = Machine-like uniformity

2. **Lexical Diversity** — How varied your vocabulary is
   - ↑ High = Rich, unique word choices
   - ↓ Low = Repetitive, formulaic vocabulary

3. **Syntactic Complexity** — How sophisticated your sentence structures are
   - ↑ High = Complex, varied structures
   - ↓ Low = Simple, repetitive patterns

4. **AI-ism Likelihood** — How many AI-characteristic phrases you use
   - ↑ High = Formulaic AI patterns detected
   - ↓ Low = Natural, human-like language

5. **Function Word Ratio** — How much grammatical scaffolding appears
   - ↑ High = Over-scaffolded, AI-like structure
   - ↓ Low = Content-heavy, human-like wording

6. **Discourse Marker Density** — How often explicit connectors appear
   - ↑ High = Over-signposted structure
   - ↓ Low = Implicit, natural flow

7. **Information Density** — How specific content is per word
   - ↑ High = Concrete, efficient wording
   - ↓ Low = Verbose, generic phrasing

8. **Epistemic Hedging** — How often uncertainty is expressed
   - ↑ High = Nuanced, human-like hedging
   - ↓ Low = Overconfident, AI-like tone

### Step 3: Visualize the Differences
- **Radar chart**: See all 8 metrics at a glance
- **Bar charts**: Compare original vs. edited side-by-side
- **Text diff**: Highlight what changed
- **Recommendations**: Get actionable suggestions

### Step 4: Export Your Report
Download analysis in formats suitable for your needs:
- **PDF**: Professional report (17 pages, charts, formatted)
- **Excel**: Data-ready workbook for statistical analysis
- **Word**: Editable document with track changes
- **PowerPoint**: Presentation slides
- **CSV/JSON**: Raw data for SPSS, R, Python analysis

---

## Understanding Your Results

### Scenario 1: Large Decrease in Burstiness
**What it means:** AI made your sentences more uniform in length.
- Original: Mix of short (3 words) and long (25 words) sentences
- Edited: Most sentences now 15-18 words

**Is this bad?**
- ✓ Better readability (AI's goal)
- ✗ Loss of authentic variation (your voice is less unique)

**What to do:**
Keep some original short sentences for emphasis. They make your writing more dynamic.

---

### Scenario 2: Drop in Lexical Diversity
**What it means:** AI replaced your varied vocabulary with common academic phrases.
- Original: "I investigated," "I discovered," "I found evidence"
- Edited: "It is important to note," "Furthermore," "In conclusion"

**Is this bad?**
- ✓ More "professional" sounding
- ✗ Less representative of your actual vocabulary level

**What to do:**
Restore some original word choices—they show your authentic voice and vocabulary growth.

---

### Scenario 3: AI-ism Score Doubled
**What it means:** AI introduced a lot of formulaic phrases common in AI-generated text.
- Examples: "It is important to note," "delve into," "in light of"

**Is this bad?**
- ✗ Plagiarism detectors flag high AI-ism as suspicious
- ✗ Instructors may question authorship
- ✗ Your voice is less authentic

**What to do:**
Edit the AI's suggestions. Replace formulaic phrases with your own words, especially in openings and closings.

---

## Interpreting the Benchmarks

VoiceTracer compares your metrics against these baselines:

| Benchmark | Burstiness | Lexical Div. | Syntactic | AI-ism | FWR | DMD | Info Density | Hedging |
|-----------|-----------|-------------|----------|---------|-----|-----|--------------|---------|
| **Native Speaker** | 1.45 | 0.68 | Moderate | 5% | 0.52 | 9 | 0.62 | 0.11 |
| **L2 Unassisted** | 1.23 | 0.55 | Moderate | 3% | 0.50 | 8 | 0.58 | 0.09 |
| **AI-Edited (ChatGPT)** | 0.78 | 0.42 | Moderate | 79% | 0.60 | 18 | 0.42 | 0.04 |

**How to read this:**
- Your unassisted writing is probably closer to the "L2 Unassisted" row
- If your edited text looks like the "AI-Edited" row, AI heavily rewrote your work
- Ideal: Keep "L2 Unassisted" characteristics while improving grammar

---

## Tips for Using VoiceTracer Effectively

### Before Editing with AI:
1. Write your first draft naturally
2. Run VoiceTracer on the unassisted version to establish your baseline
3. Use AI to fix grammar, not to rewrite everything

### When Using AI:
- Tell the AI: **"Fix grammar and punctuation only"** (not "improve my writing")
- Avoid: "Make this more professional" (leads to homogenization)
- Review: Always read the AI suggestions before accepting them

### After Getting AI Edits:
1. Run VoiceTracer to see what changed
2. Accept improvements in grammar/clarity
3. Revert changes that affect your unique voice (unusual word choices, sentence structures)
4. Aim for: Better grammar **without** losing your voice

### For Your Instructor or Advisor:
- Export your VoiceTracer report as evidence of authorship
- Show that you used AI for grammar, not content creation
- Demonstrate that your voice is still present in the final text

---

## Metrics Explained in Depth

### Burstiness Index

**What is it?**
Burstiness measures the **variation in sentence lengths**. 

**Formula:**
`Burstiness = Standard Deviation of sentence lengths / Mean sentence length`

**Example:**
```
Original sentences: 5 words, 20 words, 4 words, 18 words
- Mean = 11.75 words
- Std Dev = 7.86
- Burstiness = 7.86 / 11.75 = 0.67 (moderate variation)

Edited sentences: 12 words, 13 words, 12 words, 12 words
- Mean = 12.25 words
- Std Dev = 0.43
- Burstiness = 0.43 / 12.25 = 0.04 (very uniform)
```

**Interpretation:**
- 0.0–0.5: Very uniform (AI-like)
- 0.5–1.0: Moderate variation (balanced)
- 1.0+: High variation (human-like)

**Why it matters for your thesis:**
AI models optimize for readability by standardizing sentence structure. Humans naturally vary sentence lengths for emphasis and rhythm.

---

### Lexical Diversity

**What is it?**
Lexical diversity measures how **varied your vocabulary** is.

**Method:**
Uses MTLD (Mean Type-Token Ratio Dynamics)
- Counts unique words vs. total words
- Robust to text length
- Accounts for natural repetition of common words

**Example:**
```
Text A (diverse): "The cat, dog, and bird sang, danced, and flew."
- Many unique words, some repetition
- Diversity: 0.65 (high)

Text B (repetitive): "The important thing is that important research shows important results."
- Repetitive word choices
- Diversity: 0.35 (low)
```

**Interpretation:**
- 0.0–0.3: Very low diversity (formulaic, repetitive)
- 0.3–0.6: Moderate diversity (balanced)
- 0.6–1.0: High diversity (varied vocabulary)

---

### Syntactic Complexity

**What is it?**
Syntactic complexity measures how **sophisticated your sentence structures** are.

**Components (weighted):**
1. Average sentence length (40%)
2. Subordination ratio (30%) — how many dependent clauses you use
3. Modifier density (30%) — use of adjectives and adverbs

**Example:**
```
Simple: "I studied. I wrote. I submitted."
- Short sentences, no dependent clauses, no modifiers
- Complexity: 0.25 (low)

Complex: "Although I studied extensively, I wrote carefully and submitted my work thoughtfully."
- Longer sentence, dependent clause, modifiers
- Complexity: 0.75 (high)
```

---

### AI-ism Likelihood

**What is it?**
AI-ism likelihood detects **phrases and patterns typical of AI-generated text**.

**Categories detected:**
1. **Opening hedges**: "It is important to note that...", "One could argue..."
2. **Closing phrases**: "In conclusion...", "To summarize..."
3. **Formulaic connectors**: "delve into", "shed light on", "pave the way"
4. **Repetitive patterns**: Unusual punctuation uniformity, passive voice overuse

**Example:**
```
Text with high AI-ism:
"It is important to note that artificial intelligence represents a significant paradigm shift. 
In light of recent research, we must delve into the implications. In conclusion, 
further investigation is warranted."

Score: 78/100 (likely AI-generated or heavily AI-edited)
```

**Why it matters:**
- High scores trigger plagiarism detection systems
- Instructors recognize these patterns as non-human
- Your authentic voice is lost in formulaic language

---

## Troubleshooting

### "My metrics look very different from the benchmarks"

**Normal?** Yes! Benchmarks are averages. Your writing style is unique.
- Compare your **original vs. edited** metrics, not against benchmarks
- Look at the **direction and magnitude of change**

### "The AI-ism score is very high even though I wrote it"

**Possible reasons:**
1. You used formal academic language naturally (high score doesn't always mean AI)
2. You borrowed phrasing from textbooks/papers (this can also boost AI-ism score)
3. The text is naturally formulaic (happens with technical writing)

**Solution:** Review the detected AI-isms. If they're not actually AI-generated phrases, the score might be a false positive.

### "I want to see what changed between original and edited"

**Use Step 3: Visualizations**
- The diff view shows side-by-side text comparison
- Changed sections are highlighted
- Helps you spot where AI rewrote vs. corrected

---

## For Instructors & Advisors

### Using VoiceTracer in Your Course

**For teaching voice awareness:**
- Show students how their writing changes with AI
- Discuss the trade-offs between correctness and authenticity
- Have students write unedited → get AI help → analyze with VoiceTracer

**For assessing authorship:**
- Ask students to provide VoiceTracer reports with submissions
- High AI-ism + other indicators suggest AI-heavy rewriting
- Low AI-ism + high retained voice suggests authentic use of grammar tools

**For thesis research:**
If your students are researching AI, writing, or L2 learning:
- VoiceTracer generates publication-ready data
- Export CSV/JSON for statistical analysis
- Use as measurement tool in your own studies

---

## Data Privacy & Security

- **Your texts are NOT stored** unless you explicitly save/export
- **No analytics** — VoiceTracer doesn't track usage
- **Local processing** — all analysis happens on your device
- **Open source** — code is transparent and auditable
- **For deployment**: Optional SQLite database stored locally for session recovery

---

## Citation

If you use VoiceTracer for research or academic work:

```
VoiceTracer: A Tool for Measuring Stylistic Homogenization in L2 Academic Writing
Developed to support thesis research on AI's impact on learner voice.
Version 0.1.0 (2026)
https://github.com/VoiceTracer
```

---

## Getting Help

**Questions about specific metrics?**
→ See "Understanding Your Results" section above

**Technical issues?**
→ Check GitHub issues: https://github.com/VoiceTracer/issues

**Want to contribute?**
→ Contribute to the open-source project on GitHub

**Have an idea for improvement?**
→ Open a feature request on GitHub

---

## Next Steps

1. **Try a sample**: Click "Load Example" in Step 1 to see how VoiceTracer works
2. **Analyze your work**: Upload your own original and edited texts
3. **Review your metrics**: Understand what changed and why
4. **Export your report**: Use data for your thesis, portfolio, or coursework
5. **Iterate**: Edit your AI suggestions and re-analyze to see improvements

---

*Happy analyzing! Remember: The goal is not to avoid AI help, but to use it wisely while preserving your authentic voice as an L2 writer.*
