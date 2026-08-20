"""Unit tests for shared source-helper functions in sources/base.py."""

from __future__ import annotations

from paper_search.sources.base import (
    as_int,
    author_name,
    content_value,
    dblp_authors,
    strip_jats,
    year_from_date_parts,
    year_from_epoch_ms,
    year_from_iso,
    year_from_pubdate,
)


def test_as_int_handles_str_int_and_none() -> None:
    assert as_int("2021") == 2021
    assert as_int(2021) == 2021
    assert as_int(None) is None


def test_as_int_rejects_invalid_values() -> None:
    assert as_int("nope") is None
    assert as_int([]) is None


def test_year_from_iso_extracts_year() -> None:
    assert year_from_iso("2024-03-01T00:00:00Z") == 2024
    assert year_from_iso("") is None


def test_year_from_pubdate_parses_pubmed_style_date() -> None:
    assert year_from_pubdate("2024 Jan 05") == 2024
    assert year_from_pubdate("garbage") is None


def test_year_from_epoch_ms_converts_timestamp() -> None:
    assert year_from_epoch_ms(1577880000000) == 2020
    assert year_from_epoch_ms(None) is None


def test_year_from_date_parts_reads_first_date() -> None:
    issued = {"date-parts": [[2022, 3]]}
    assert year_from_date_parts(issued) == 2022
    assert year_from_date_parts(None) is None
    assert year_from_date_parts({"date-parts": []}) is None


def test_strip_jats_removes_xml_tags_and_collapses_space() -> None:
    raw = "<jats:p>Abstract <jats:bold>with</jats:bold>  tags.</jats:p>"
    assert strip_jats(raw) == "Abstract with tags."
    assert strip_jats(None) is None


def test_author_name_formats_person_and_organization() -> None:
    assert author_name({"given": "Dana", "family": "Smith"}) == "Dana Smith"
    assert author_name({"name": "Institute of Science"}) == "Institute of Science"


def test_dblp_authors_normalizes_list_dict_and_single() -> None:
    assert dblp_authors({"author": [{"text": "Jack"}, {"text": "Kim"}]}) == ["Jack", "Kim"]
    assert dblp_authors({"author": {"text": "Liam"}}) == ["Liam"]
    assert dblp_authors({"author": "Solo"}) == ["Solo"]
    assert dblp_authors(None) == []


def test_content_value_unwraps_openreview_v2_field() -> None:
    assert content_value({"value": "title"}) == "title"
    assert content_value("plain") == "plain"
