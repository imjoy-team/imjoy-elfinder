"""Provide pytest fixtures.."""
import shutil

import pytest
from pyramid import testing

from . import ROOT_PATH, TEST_CONTENT


@pytest.fixture(name="p_config", autouse=True)
def config_fixture(settings):
    """Provide a mock pyramid Configurator instance.

    This also sets up and tearsdown the context before and after the test.
    """
    with testing.testConfig() as config:
        config.add_settings(settings)
        yield config


@pytest.fixture(name="p_request")
def request_fixture():
    """Provide a mock pyramid Request instance."""
    request = testing.DummyRequest()
    return request


@pytest.fixture(name="settings")
def settings_fixture(tmp_path):
    """Provide default settings for the app."""
    settings = {
        "root_dir": str(tmp_path),
        "files_url": "/files",
        "base_url": "",
        "expose_real_path": True,
        "thumbnail_dir": ".tmb",
    }
    return settings


@pytest.fixture(name="txt_file")
def txt_file_fixture(tmp_path):
    """Provide a temporary text file."""
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir()
    fil = tmp_dir / "test.txt"
    fil.write_text(TEST_CONTENT)
    yield fil


@pytest.fixture(name="jpeg_file")
def jpeg_file_fixture(tmp_path):
    """Provide a temporary text file."""
    fly_img = ROOT_PATH / "example-data" / "fly.jpeg"
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir()
    test_fil = tmp_dir / "test.jpeg"
    shutil.copyfile(fly_img, test_fil)
    yield test_fil
