"""
loader.py

Reads concepts.yaml and every file under frameworks/ into plain Python
data structures. Kept deliberately simple (no ORM, no database) — the
whole point of this project is that the data is human-readable YAML that
a compliance person, not just an engineer, could review and edit.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CONCEPTS_FILE = REPO_ROOT / "concepts.yaml"
FRAMEWORKS_DIR = REPO_ROOT / "frameworks"


@dataclass
class Concept:
    id: str
    name: str
    description: str


@dataclass
class Obligation:
    id: str
    citation: str
    title: str
    summary: str
    concepts: list[str]
    framework_id: str
    framework_name: str


@dataclass
class CrosswalkData:
    concepts: dict[str, Concept] = field(default_factory=dict)
    obligations: list[Obligation] = field(default_factory=list)
    frameworks: dict[str, dict] = field(default_factory=dict)

    def obligations_for_concept(self, concept_id: str) -> list[Obligation]:
        return [o for o in self.obligations if concept_id in o.concepts]

    def concept_matrix(self) -> dict[str, dict[str, list[Obligation]]]:
        """Return {concept_id: {framework_id: [Obligation, ...]}}."""
        matrix: dict[str, dict[str, list[Obligation]]] = {
            cid: {fid: [] for fid in self.frameworks} for cid in self.concepts
        }
        for obligation in self.obligations:
            for cid in obligation.concepts:
                if cid not in matrix:
                    # Obligation references a concept ID that doesn't exist
                    # in concepts.yaml — surface this loudly rather than
                    # silently dropping it.
                    raise ValueError(
                        f"Obligation '{obligation.id}' references unknown "
                        f"concept '{cid}'. Add it to concepts.yaml or fix "
                        f"the typo in {obligation.framework_id}.yaml."
                    )
                matrix[cid][obligation.framework_id].append(obligation)
        return matrix


def load_concepts() -> dict[str, Concept]:
    with open(CONCEPTS_FILE, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return {
        c["id"]: Concept(id=c["id"], name=c["name"], description=c["description"].strip())
        for c in raw["concepts"]
    }


def load_frameworks() -> tuple[dict[str, dict], list[Obligation]]:
    frameworks: dict[str, dict] = {}
    obligations: list[Obligation] = []

    for path in sorted(FRAMEWORKS_DIR.glob("*.yaml")):
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        fw = raw["framework"]
        frameworks[fw["id"]] = fw

        for o in raw.get("obligations", []):
            obligations.append(
                Obligation(
                    id=o["id"],
                    citation=o["citation"],
                    title=o["title"],
                    summary=o["summary"].strip(),
                    concepts=list(o["concepts"]),
                    framework_id=fw["id"],
                    framework_name=fw["name"],
                )
            )

    return frameworks, obligations


def load_all() -> CrosswalkData:
    concepts = load_concepts()
    frameworks, obligations = load_frameworks()
    return CrosswalkData(concepts=concepts, obligations=obligations, frameworks=frameworks)
