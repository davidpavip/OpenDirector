import pytest

from opendirector.core.timestamp import Timestamp


def test_parse_srt_comma():
    ts = Timestamp.parse("00:01:13,500")
    assert ts.milliseconds == 73500
    assert str(ts) == "00:01:13,500"


def test_parse_srt_dot():
    ts = Timestamp.parse("00:01:13.500")
    assert str(ts) == "00:01:13,500"


def test_parse_numeric_seconds_string():
    ts = Timestamp.parse("73.5")
    assert str(ts) == "00:01:13,500"


def test_parse_float_seconds():
    ts = Timestamp.parse(73.5)
    assert str(ts) == "00:01:13,500"


def test_parse_int_milliseconds():
    ts = Timestamp.parse(73500)
    assert str(ts) == "00:01:13,500"


def test_addition():
    ts = Timestamp.parse("00:00:10,000") + "00:00:04,500"
    assert str(ts) == "00:00:14,500"


def test_subtraction():
    ts = Timestamp.parse("00:00:10,000") - "00:00:04,500"
    assert str(ts) == "00:00:05,500"


def test_negative_result_rejected():
    with pytest.raises(ValueError):
        Timestamp.parse("00:00:01,000") - "00:00:02,000"


def test_sorting():
    items = [
        Timestamp.parse("00:00:03,000"),
        Timestamp.parse("00:00:01,000"),
        Timestamp.parse("00:00:02,000"),
    ]
    assert [str(x) for x in sorted(items)] == [
        "00:00:01,000",
        "00:00:02,000",
        "00:00:03,000",
    ]


def test_invalid_format():
    with pytest.raises(ValueError):
        Timestamp.parse("bad timestamp")
