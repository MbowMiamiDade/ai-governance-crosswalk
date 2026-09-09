"""
search.py

Two ways to find obligations:

1. by_concept(): exact lookup by concept ID (or name). This is the core
   "crosswalk" behavior — pick a governance concern, see every framework's
   obligation for it, side by side.

2. by_free_text(): a lightweight semantic-ish search using TF-IDF + cosine
   similarity (scikit-learn), so a user can type something like "third
   party vendor oversight" and get relevant obligations even if the exact
   wording doesn't match a concept name. No external model downloads
   required, which keeps this dependency-light and fully offline.
"""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .loader import CrosswalkData, Obligation


def by_concept(data: CrosswalkData, concept_query: str) -> list[Obligation]:
    """Look up obligations by concept ID (exact) or concept name (case-insensitive)."""
    concept_query_lower = concept_query.strip().lower()

    # Exact ID match first
    if concept_query in data.concepts:
        return data.obligations_for_concept(concept_query)

    # Fall back to matching on concept name
    for cid, concept in data.concepts.items():
        if concept.name.lower() == concept_query_lower:
            return data.obligations_for_concept(cid)

    raise KeyError(
        f"No concept found matching '{concept_query}'. "
        f"Run `python cli.py --list-concepts` to see valid options."
    )


@dataclass
class ScoredObligation:
    obligation: Obligation
    score: float


def by_free_text(data: CrosswalkData, query: str, top_n: int = 8) -> list[ScoredObligation]:
    """
    Rank all obligations against a free-text query using TF-IDF cosine
    similarity over each obligation's title + summary + concept names.
    """
    corpus_texts = []
    for o in data.obligations:
        concept_names = " ".join(data.concepts[cid].name for cid in o.concepts if cid in data.concepts)
        corpus_texts.append(f"{o.title} {o.summary} {concept_names}")

    vectorizer = TfidfVectorizer(stop_words="english")
    doc_vectors = vectorizer.fit_transform(corpus_texts)
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(query_vector, doc_vectors)[0]

    scored = [
        ScoredObligation(obligation=o, score=float(score))
        for o, score in zip(data.obligations, similarities)
        if score > 0
    ]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored[:top_n]


def concept_matrix_markdown(data: CrosswalkData) -> str:
    """Render the full concept x framework crosswalk as a Markdown table."""
    framework_ids = sorted(data.frameworks.keys())
    matrix = data.concept_matrix()

    lines = []
    header = ["Concept"] + [data.frameworks[fid]["name"] for fid in framework_ids]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))

    for cid, concept in sorted(data.concepts.items(), key=lambda kv: kv[1].name):
        row = [concept.name]
        for fid in framework_ids:
            obligations = matrix[cid][fid]
            if obligations:
                # Multiple distinct obligations can share the same citation
                # (e.g. three different SR 26-2 controls all living in
                # Section VI). Dedupe for the matrix view only — the
                # underlying records, and `--concept` lookup, still show
                # every obligation individually.
                seen = []
                for o in obligations:
                    if o.citation not in seen:
                        seen.append(o.citation)
                cell = "<br>".join(seen)
            else:
                cell = "—"
            row.append(cell)
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)
