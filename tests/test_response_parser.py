import pytest

from app.llm.response_parser import (
    normalize_to_list,
    parse_json_response,
    safe_get_list,
)


def test_parse_clean_json_object() -> None:
    assert parse_json_response('{"a": 1}') == {"a": 1}


def test_parse_json_from_markdown_fence() -> None:
    assert parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_json_with_extra_text() -> None:
    assert parse_json_response('Here it is:\n{"a": 1}\nThanks') == {"a": 1}


def test_parse_json_array() -> None:
    assert parse_json_response('[{"a": 1}]') == [{"a": 1}]


def test_invalid_json_raises_value_error() -> None:
    with pytest.raises(ValueError):
        parse_json_response("not json")


def test_normalize_to_list() -> None:
    assert normalize_to_list(None) == []
    assert normalize_to_list(["a"]) == ["a"]
    assert normalize_to_list("a") == ["a"]


def test_safe_get_list() -> None:
    assert safe_get_list({"items": [1]}, "items") == [1]
    assert safe_get_list({"items": "bad"}, "items") == []
    assert safe_get_list({}, "items") == []
