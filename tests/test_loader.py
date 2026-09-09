"""
Basic data-integrity tests. These aren't testing AI models — they're
testing that the YAML data files are internally consistent, which matters
a lot for a crosswalk tool where a typo'd concept ID would silently break
the whole point of the project.
"""

import pytest

from crosswalk.loader import load_all
from crosswalk.search import by_concept, by_free_text, concept_matrix_markdown


@pytest.fixture(scope="module")
def data():
    return load_all()


def test_frameworks_loaded(data):
    assert len(data.frameworks) == 4
    expected_ids = {"nist_ai_rmf", "eu_ai_act", "sr_26_2", "cri_fs_ai_rmf"}
    assert set(data.frameworks.keys()) == expected_ids


def test_concepts_loaded(data):
    assert len(data.concepts) >= 10


def test_every_obligation_has_at_least_one_concept(data):
    for o in data.obligations:
        assert len(o.concepts) >= 1, f"{o.id} has no concepts tagged"


def test_every_obligation_concept_id_exists(data):
    # This will raise ValueError inside concept_matrix() if any obligation
    # references a concept ID that isn't defined in concepts.yaml.
    data.concept_matrix()


def test_every_obligation_has_required_fields(data):
    for o in data.obligations:
        assert o.id
        assert o.citation
        assert o.title
        assert o.summary
        assert o.framework_id
        assert o.framework_name


def test_by_concept_exact_id(data):
    results = by_concept(data, "human_oversight")
    assert len(results) > 0
    assert all("human_oversight" in o.concepts for o in results)


def test_by_concept_name_case_insensitive(data):
    results = by_concept(data, "human oversight")
    assert len(results) > 0


def test_by_concept_unknown_raises(data):
    with pytest.raises(KeyError):
        by_concept(data, "not_a_real_concept")


def test_by_free_text_returns_results(data):
    results = by_free_text(data, "third party vendor oversight")
    assert len(results) > 0
    # top result should be reasonably relevant
    assert results[0].score > 0


def test_concept_matrix_markdown_renders(data):
    md = concept_matrix_markdown(data)
    assert "| Concept |" in md
    assert "NIST AI Risk Management Framework" in md
