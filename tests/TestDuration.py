import pytest

from UM.Qt.Duration import Duration, DurationFormat

test_data = [
    {"total_time": 22, "seconds": 22, "minutes": 0, "hours": 0, "days": 0},
    {"total_time": 60, "seconds": 0, "minutes": 1, "hours": 0, "days": 0},
    {"total_time": 3600, "seconds": 0, "minutes": 0, "hours": 1, "days": 0},
    {"total_time": 86400, "seconds": 0, "minutes": 0, "hours": 0, "days": 1},
    {"total_time": 90061, "seconds": 1, "minutes": 1, "hours": 1, "days": 1},
]

@pytest.mark.parametrize("data", test_data)
def test_durationCreation(data):
    duration = Duration(data["total_time"])
    assert duration.days == data["days"]
    assert duration.seconds == data["seconds"]
    assert duration.minutes == data["minutes"]
    assert duration.hours == data["hours"]
    assert int(duration) == data["total_time"]
    assert duration.valid
    assert not duration.isTotalDurationZero

def test_invalidDuration():
    duration = Duration()
    assert not duration.valid


def test_zeroDuration():
    zero_duration = Duration(0)
    assert zero_duration.isTotalDurationZero
    assert zero_duration.valid


def test_negativeDuration():
    negative_duration = Duration(-10)
    assert not negative_duration.valid


def test_hugeDuration():
    duration = Duration(2147483648)
    # Reaaaaaaly big numbers should be reset to zero because of python C++ conversion issues.
    assert duration.isTotalDurationZero


def test_getDisplayString():
    # We only test the ones that are not depending on translations.
    assert Duration(1).getDisplayString(DurationFormat.Format.Seconds) == "1"
    assert Duration(1).getDisplayString(9002) == ""  # Unkown format.
    assert Duration(1).getDisplayString(DurationFormat.Format.ISO8601) == "00:00:01"
    assert Duration(86401).getDisplayString(DurationFormat.Format.ISO8601) == "24:00:01"