---
name: ss-ml-paper-writing
description: >-
  Write publication-ready ML/AI/Systems papers for NeurIPS, ICML, ICLR, ACL,
  AAAI, COLM, OSDI, NSDI, ASPLOS, SOSP. Use when drafting papers from research
  repos, structuring arguments, verifying citations, or preparing camera-ready
  submissions. Includes LaTeX templates and reviewer guidelines.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
  - WebSearch
  - Agent
metadata:
  source: K-Dense-AI/claude-scientific-skills
  depends-on: ss-arxiv-database ss-citation-cff
---

# ML Paper Writing

Produce publication-ready papers for top ML, AI, and systems venues. Follows
reviewer expectations for each conference and enforces consistent structure,
citation hygiene, and LaTeX formatting.

---

## Supported Venues

| Track | Venues |
|-------|--------|
| ML/AI | NeurIPS, ICML, ICLR, AAAI, COLM |
| NLP | ACL, EMNLP, NAACL |
| Systems | OSDI, NSDI, ASPLOS, SOSP, EuroSys |

---

## Phase 1 — Understand the Contribution

Before writing, extract the paper's core claim:

1. **Read** the research repo: results, configs, README, notebooks.
2. **Identify** the single sentence that captures the contribution.
3. **List** 3–5 evidence points (tables, figures, ablations) that support it.
4. **Determine** the target venue and load its formatting requirements (see Phase 5).

Write a one-page outline to `paper/outline.md` before drafting.

---

## Phase 2 — Structure

Standard ML paper structure (adapt per venue):

```
Abstract          — 150–250 words; problem, method, result, significance
1. Introduction   — motivation, gap, contribution list, paper roadmap
2. Related Work   — group by theme; distinguish from your approach
3. Method         — notation, model, algorithm; self-contained
4. Experiments    — datasets, baselines, metrics, main results, ablations
5. Analysis       — error analysis, qualitative examples, limitations
6. Conclusion     — summary, broader impact, future work
References
Appendix          — proofs, extended tables, reproducibility details
```

Systems papers swap Section 2–3 for Design + Implementation.

---

## Phase 3 — Writing Guidelines

### Abstract
- Sentence 1: the problem.
- Sentence 2: why existing solutions fail.
- Sentences 3–4: your approach in plain language.
- Sentence 5: headline result with a number.
- Sentence 6: significance / broader impact.

### Introduction
- Open with a concrete motivating example, not a generic statement.
- State contributions as a bulleted list at the end.
- Use present tense for your contributions; past tense for prior work.

### Method
- Define all notation in a table or dedicated paragraph before using it.
- Every equation should be referenced in prose.
- Include a system diagram or algorithm box.

### Experiments
- Lead with the main result table.
- Bold the best result in each column.
- Include error bars or confidence intervals.
- Ablation table must isolate one variable per row.

### Writing style
- Active voice, short sentences, no hedging.
- Avoid: "In this paper, we propose…" (say "We propose…").
- Avoid: "very", "quite", "somewhat", "interesting".
- Every claim needs a citation or evidence pointer.

---

## Phase 4 — Citation Hygiene

1. Use BibTeX; never cite URLs directly in text.
2. Verify each citation with `ss-arxiv-database` or WebSearch.
3. Prefer arXiv IDs for preprints; use published venue entries when available.
4. Run deduplication: `bibtool -s -d references.bib -o references_clean.bib`
5. Check for missing venue/year fields before submission.

---

## Phase 5 — Venue-Specific Requirements

### Loading Style Files
```bash
# NeurIPS
wget https://neurips.cc/media/neurips-2024.sty

# ICML
wget https://icml.cc/media/icml2024.sty

# ICLR — uses openreview template
# ACL — use acl_latex.sty from aclpub
```

Or use WebFetch to retrieve the current year's author kit from the venue site.

### Page Limits (verify for current year)
| Venue | Main | + References | Appendix |
|-------|------|-------------|---------|
| NeurIPS | 9 | unlimited | unlimited |
| ICML | 8 | unlimited | unlimited |
| ICLR | 8 | unlimited | unlimited |
| ACL | 8 | unlimited | unlimited |
| OSDI/SOSP | 12 | included | — |

### Reviewer Expectations by Venue
- **NeurIPS/ICML/ICLR**: theory or strong empirical novelty; reproducibility checklist required.
- **ACL**: linguistic motivation; include human evaluation for generation tasks.
- **OSDI/SOSP/ASPLOS**: real system with eval on production-scale workloads; no toy benchmarks.

---

## Phase 6 — Camera-Ready Checklist

- [ ] All author names, affiliations, and emails correct
- [ ] Acknowledgments section includes grants and compute credits
- [ ] All figures are vector (PDF/EPS) at ≥ 300 DPI
- [ ] No `\TODO` or `\FIXME` macros remain
- [ ] Bibliography sorted and deduplicated
- [ ] Supplementary material compiles standalone
- [ ] Reproducibility checklist completed (NeurIPS/ICML/ICLR)
- [ ] PDF passes venue accessibility checker (NeurIPS requires it)
- [ ] File size within venue limit (usually 50 MB)

---

## LaTeX Snippets

### Algorithm block
```latex
\usepackage{algorithm, algpseudocode}

\begin{algorithm}
\caption{Your Algorithm}
\begin{algorithmic}[1]
  \Require input $x$
  \State $y \gets f(x)$
  \Return $y$
\end{algorithmic}
\end{algorithm}
```

### Table with bold best result
```latex
\begin{table}[t]
\centering
\caption{Main results on benchmark X.}
\begin{tabular}{lcc}
\toprule
Method & Metric A & Metric B \\
\midrule
Baseline & 72.1 & 81.3 \\
\textbf{Ours} & \textbf{78.4} & \textbf{85.7} \\
\bottomrule
\end{tabular}
\end{table}
```
