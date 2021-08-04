
from unittest.mock import patch, MagicMock
import pytest
import json
import UpdateChecker as uc

from UM.Version import Version
from ..UpdateChecker import UpdateChecker
import os

test_path = os.path.join(os.path.dirname(uc.__file__), "tests")
def loadDataFile(file_name):
    path = os.path.join(test_path, file_name)
    with open(path) as f:
        return json.load(f)


data_files = [loadDataFile("CuraOnly1-0-0.json"),
              loadDataFile("CuraAndCuraBeta1-0-0.json")
              ]

normal_url = "https://www.ultimaker.com"
beta_url = "https://www.ultimaker.com/beta"

@pytest.fixture
def update_checker():
    application = MagicMock()
    preferences = MagicMock(name ="preferences")
    application.getPreferences = MagicMock(return_value = preferences)
    with patch("UM.TaskManagement.HttpRequestManager.HttpRequestManager.getInstance"):
        with patch("UM.Application.Application.getInstance", MagicMock(return_value = application)):
            return UpdateChecker()

@pytest.mark.parametrize(
    "data,              application_name,   expected_version,   expected_url", [
    (data_files[0],     "cura",             "1.0.0",            normal_url),
    (data_files[0],     "whatever",         None,               None),
    (data_files[0],     "cura-beta",        None,               None),  # Old file, so beta shouldn't be found!
    (data_files[1],     "cura-beta",        "1.0.0",            beta_url),
    (data_files[1],     "cura",             "1.0.0",            normal_url),
    (data_files[1],     "whatever",         None,               None)
    ])
def test__extractVersionAndURLFromData(data, application_name, expected_version, expected_url):
    version, update_url = UpdateChecker._extractVersionAndURLFromData(data, application_name)
    if expected_version is None:
        assert version is None
    else:
        assert version == Version(expected_version)
    if update_url is None:
        assert update_url is None
    else:
        assert update_url == expected_url

@pytest.mark.parametrize(
    "local_version, latest_version, latest_version_shown,   display_same_version,   result", [
    ("1.0.0",       "1.0.0",        "0.0.0",                True,                   True),
    ("0.0.0",       "1.0.0",        "0.0.0",                False,                  True),
    ("1.0.0",       "1.0.0",        "1.0.0",                False,                  False),
    ("1.0.0",       "1.0.0",        "1.0.0",                True,                   True),
    ("2.0.0",       "1.0.0",        "1.0.0",                True,                   False),
    ("0.5.0",       "1.0.0",        "1.0.0",                False,                  False),
])
def test__handleLatestUpdate(update_checker, local_version, latest_version, latest_version_shown, display_same_version, result):
    local_version = Version(local_version)
    latest_version = Version(latest_version)
    latest_version_shown = Version(latest_version_shown)
    message_class = MagicMock()
    preference_key = "whatever"

    application = MagicMock()
    preferences = MagicMock(name = "preferences")
    application.getPreferences = MagicMock(return_value = preferences)
    preferences.getValue = MagicMock(return_value = latest_version_shown)
    with patch("UM.Application.Application.getInstance", MagicMock(return_value=application)):
        assert update_checker._handleLatestUpdate(local_version, latest_version, False, display_same_version, message_class, preference_key) == result
