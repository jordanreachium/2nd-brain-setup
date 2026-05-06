from __future__ import annotations
from lib.ids import kebab_slug


def test_basic():
    assert kebab_slug("Hello World") == "hello-world"


def test_strips_punctuation():
    assert kebab_slug("Foo & Bar #1!") == "foo-bar-1"


def test_collapses_whitespace():
    assert kebab_slug("foo   bar\n\tbaz") == "foo-bar-baz"


def test_collapses_multiple_dashes():
    assert kebab_slug("foo---bar--baz") == "foo-bar-baz"


def test_strips_leading_trailing_dashes():
    assert kebab_slug("---foo bar---") == "foo-bar"


def test_empty_input_returns_empty_string():
    assert kebab_slug("") == ""


def test_only_punctuation_returns_empty_string():
    assert kebab_slug("!!!???") == ""


def test_unicode_letters_kept_lowercase():
    assert kebab_slug("Café Résumé") == "café-résumé"
