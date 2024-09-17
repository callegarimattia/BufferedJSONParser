import pytest

from src.solution import StreamingJsonParser


@pytest.fixture
def parser():
    return StreamingJsonParser()


def test_streaming_json_parser(parser):
    parser.consume('{"foo": "bar"}')
    assert parser.get() == {"foo": "bar"}


def test_chunked_streaming_json_parser(parser):
    parser.consume('{"foo":')
    parser.consume('"bar')
    assert parser.get() == {"foo": "bar"}


def test_partial_streaming_json_parser(parser):
    parser.consume('{"foo": "bar')
    assert parser.get() == {"foo": "bar"}


def test_more_pairs(parser):
    parser.consume('{"foo": "bar", "foobar" : "barfoo"}')
    assert parser.get() == {"foo": "bar", "foobar": "barfoo"}


def test_partial_more_pairs(parser):
    parser.consume('{"foo": "bar", "foobar" : "ba')
    assert parser.get() == {"foo": "bar", "foobar": "ba"}


def test_dictionary(parser):
    parser.consume('{"foo": {"bar": "baz"} }')
    assert parser.get() == {"foo": {"bar": "baz"}}


def test_dictionary_recursive(parser):
    parser.consume('{"foo": {"bar": {"foobar":"foobaz"} } }')
    assert parser.get() == {"foo": {"bar": {"foobar": "foobaz"}}}


def test_dictionary_recursive2(parser):
    parser.consume('{"foo": {"bar": {"foobar": {"foofoo": "bazbaz"} } } }')
    assert parser.get() == {"foo": {"bar": {"foobar": {"foofoo": "bazbaz"}}}}


def test_dictionary_recursive_truncated(parser):
    parser.consume('{"foo": {"bar": {"foobar":"foobaz"')
    assert parser.get() == {"foo": {"bar": {"foobar": "foobaz"}}}


def test_dictionary_recursive_truncated2(parser):
    parser.consume('{"foo": {"bar": {"foobar":"foobaz"}')
    assert parser.get() == {"foo": {"bar": {"foobar": "foobaz"}}}


def test_dictionary_recursive_truncated3(parser):
    parser.consume('{"foo": {"bar": {"foobar": {"foofoo": "bazbaz"')
    assert parser.get() == {"foo": {"bar": {"foobar": {"foofoo": "bazbaz"}}}}


def test_pair_and_partial_key(parser):
    parser.consume('{"foo": "bar", "fo')
    assert parser.get() == {"foo": "bar"}


def test_overwrite(parser):
    parser.consume('{"foo": "bar"}')
    assert parser.get() == {"foo": "bar"}
    parser.consume('{"foo": "baz"}')
    assert parser.get() == {"foo": "baz"}
