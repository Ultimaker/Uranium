
from unittest.mock import patch, MagicMock
import sys
import os

from UM.Version import Version

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import UpdateCheckerJob
import pytest


run_data = [(b'{"TestApplication" : {"testOperatingSystem": {"major": 2, "minor": 0, "revision":0, "url": ""}} }', (Version("2.0.0"), "")),
            (b'{"TestApplication" : {"testOperatingSystem": {"major": 1, "minor": 0, "revision":0, "url": ""}} }', None),
            (b'{"TestApplication" : {"testOperatingSystem2": {"major": 1, "minor": 0, "revision":0, "url": ""}, "testOperatingSystem": {"major": 2, "minor": 1, "revision":9, "url": "beep"}} }', (Version("2.1.9"), "beep")),
            (b'', None)
            ]

@pytest.mark.parametrize("request_result, show_update_called_data", run_data)
def test_run(request_result, show_update_called_data):
    job = UpdateCheckerJob.UpdateCheckerJob(url = "blarg")
    application = MagicMock()
    application.getApplicationName = MagicMock(return_value = "TestApplication")
    application.getVersion = MagicMock(return_value = "1.0.0")

    request = MagicMock()
    request.read = MagicMock(side_effect = [request_result, b''])

    platform = MagicMock()
    platform.system = MagicMock(return_value = "testOperatingSystem")
    job.showUpdate = MagicMock()
    with patch("UpdateCheckerJob.platform", platform):
        with patch("UpdateCheckerJob.urllib.request.Request"):
            with patch("UM.Application.Application.getInstance", MagicMock(return_value = application)):
                with patch("UpdateCheckerJob.urllib.request.urlopen", return_value = request):
                    job.run()
    if show_update_called_data is not None:
        job.showUpdate.assert_called_once_with(show_update_called_data[0], show_update_called_data[1])
    else:
        assert job.showUpdate.call_count == 0