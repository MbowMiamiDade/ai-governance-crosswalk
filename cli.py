#!/usr/bin/env python3
"""
cli.py

Command-line interface for the AI Governance Regulatory and Control Crosswalk.

Examples:
    python cli.py --list-concepts
    python cli.py --concept vendor_third_party_risk
    python cli.py --concept "Human Oversight"
    python cli.py --query "third party vendor oversight"
    python cli.py --matrix > output/crosswalk_matrix.md
"""

from __future__ import annotations

import argparse
import sys

from crosswalk.loader import load_all
from crosswalk.search import by_concept, by_free_text, concept_matrix_markdown


def print_obligation(o, score: float | None = None) -> None:
    header = f"[{o.framework_name}] {o.citation} — {o.title}"
    if score is not None:
        header += f"  (match: {score:.2f})"
    print(header)
    print(f"  {o.summary.strip()}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Governance Regulatory and Control Crosswalk")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--concept", help="Exact concept ID or name, e.g. 'vendor_third_party_risk' or 'Human Oversight'"
    )
    group.add_argument("--query", help="Free-text governance concern, e.g. 'third party vendor oversight'")
    group.add_argument("--list-concepts", action="store_true", help="List all available concept IDs")
    group.add_argument("--matrix", action="store_true", help="Print the full concept x framework matrix as Markdown")

    args = parser.parse_args()
    data = load_all()

    if args.list_concepts:
        for cid, concept in sorted(data.concepts.items()):
            print(f"{cid:30s} {concept.name}")
        return

    if args.matrix:
        print(concept_matrix_markdown(data))
        return

    if args.concept:
        try:
            obligations = by_concept(data, args.concept)
        except KeyError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)

        if not obligations:
            print(f"No obligations tagged with concept '{args.concept}' yet.")
            return

        print(f"=== Obligations for concept: {args.concept} ===\n")
        for o in obligations:
            print_obligation(o)
        return

    if args.query:
        results = by_free_text(data, args.query)
        if not results:
            print("No matches found. Try a different phrasing, or use --list-concepts.")
            return

        print(f'=== Top matches for: "{args.query}" ===\n')
        for scored in results:
            print_obligation(scored.obligation, score=scored.score)
        return


if __name__ == "__main__":
    main()
