# AI Governance Regulatory and Control Crosswalk

A tool that maps AI governance obligations across multiple frameworks to a
shared taxonomy of governance concerns — so instead of reading four
documents to answer "what do I need to do about vendor risk?", you ask the
question once and see every framework's answer side by side.

## Why this project

AI governance work increasingly means working across overlapping regimes:
a voluntary U.S. framework, binding EU law, sector-specific industry
guidance, and decades-old model risk supervisory expectations that never
mentioned "AI" but apply to it anyway. Nobody memorizes all four. What's
useful is a fast, honest way to compare them on a given concern.

This project treats governance controls as data, not prose — a
"compliance-as-code" approach: obligations live in structured YAML,
tagged against a shared concept taxonomy, and can be searched, tested, and
regenerated into new report formats without touching the underlying
frameworks.

## Frameworks included

| Framework | What it is | Status |
|---|---|---|
| **NIST AI RMF 1.0** | Voluntary U.S. framework (Govern/Map/Measure/Manage) | Public domain |
| **EU AI Act** (Reg. (EU) 2024/1689) | Binding EU law, risk-tiered | Public law text |
| **SR 26-2** (Fed/OCC/FDIC) | Interagency banking supervisory guidance on model risk management, issued April 2026 — supersedes SR 11-7 (2011) | Public supervisory guidance |
| **CRI FS AI RMF** | Industry-built framework for financial services (Cyber Risk Institute / FSSCC), launched Feb 2026 | Free download; 12 of 230 control objectives sampled — see note below |

### Why ISO/IEC 42001 is not included

ISO/IEC 42001 is a licensed standard — the full text isn't publicly
available to reproduce or closely paraphrase without a copy. For a
learning/demonstration project, mapping it isn't worth the IP risk. If you
want to add it later, buy or license the standard and build the mapping
from your own copy rather than from secondhand summaries.

### Note on the CRI FS AI RMF entries

The full FS AI RMF Risk and Control Matrix (Ver. 1.0, 02-09-2026) contains
230 control objectives across 19 categories. `frameworks/cri_fs_ai_rmf.yaml`
includes 12 of them — one mapped to each concept in this project's taxonomy
— not the full matrix. Citation IDs (e.g., `GV-2.3.3`) match the RCM's own
numbering, so each entry can be looked up directly against the source
spreadsheet, available at
[cyberriskinstitute.org](https://cyberriskinstitute.org/the-profile/).

## The concept taxonomy

The whole crosswalk depends on `concepts.yaml` — twelve governance
concerns (governance & accountability, data quality, human oversight,
transparency, model validation, monitoring, vendor risk, change
management, incident response, documentation, bias & fairness, risk
assessment) that every framework's obligations are tagged against. This
taxonomy is the actual intellectual work of the project — anyone can copy
four frameworks into YAML, but deciding how they line up conceptually is
the governance judgment part.

## Project structure

```
ai-governance-crosswalk/
├── concepts.yaml              # the shared taxonomy
├── frameworks/
│   ├── nist_ai_rmf.yaml
│   ├── eu_ai_act.yaml
│   ├── sr_26_2.yaml
│   └── cri_fs_ai_rmf.yaml
├── crosswalk/
│   ├── loader.py               # reads YAML into Python objects
│   └── search.py               # concept lookup + TF-IDF free-text search
├── cli.py                      # command-line interface
├── tests/
│   └── test_loader.py          # data-integrity tests
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Using Google Colab instead

The CLI above assumes a local terminal. If you work in Colab, use
`notebooks/AI_Governance_Crosswalk_Demo.ipynb` instead — it drives the same
`crosswalk/` package interactively (concept lookup, free-text search, the
full matrix rendered as Markdown, and running the test suite), with no
terminal required.

## Usage

List all governance concepts:

```bash
python cli.py --list-concepts
```

Look up every framework's obligation for a specific concern:

```bash
python cli.py --concept vendor_third_party_risk
python cli.py --concept "Human Oversight"
```

Free-text search (TF-IDF similarity — no exact concept match required):

```bash
python cli.py --query "third party vendor oversight"
```

Generate the full concept x framework crosswalk as a Markdown table:

```bash
python cli.py --matrix > output/crosswalk_matrix.md
```

Run the data-integrity tests:

```bash
pytest
```

## How obligations are written

Every obligation summary in the `frameworks/*.yaml` files is an original
paraphrase written for this project — not quoted text from the source
document. Citation fields point to the section/article so you can verify
against the primary source. Treat this repo as a study and demonstration
aid, not a compliance-grade legal mapping — always confirm against the
actual framework text before relying on any specific obligation.

## Scope and methodology

Crosswalk mappings identify conceptual alignment across selected governance
requirements and controls — they do not imply legal or regulatory
equivalence. A shared row in the matrix means the frameworks address a
similar governance concern, not that satisfying one obligation satisfies
another.

Worth noting specifically: the 2026 Interagency Model Risk Management
Guidance (SR 26-2) explicitly states that generative AI and agentic AI
models are outside its scope — its principles apply to traditional
quantitative models and non-generative, non-agentic AI models. That's a
real applicability boundary, not an oversight in this project, and it's
part of why this crosswalk includes AI-specific frameworks (NIST AI RMF,
EU AI Act) alongside it rather than relying on model risk guidance alone.

## Roadmap / possible extensions

- Streamlit front-end for non-technical browsing
- Expand the CRI FS AI RMF sample beyond the current 12 control objectives
- GitHub Actions CI to run `pytest` on every push (data-integrity checks
  catch broken concept references automatically)
- Add a "gap analysis" mode: given two frameworks, show concepts where one
  has an obligation and the other doesn't
