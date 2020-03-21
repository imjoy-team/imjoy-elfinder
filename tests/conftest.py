"""Provide pytest fixtures.."""
import pytest
from pyramid import testing

from . import ROOT_DIR


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
def settings_fixture():
    """Provide default settings for the app."""
    settings = {
        "root_dir": str(ROOT_DIR),
        "files_url": "/files",
        "base_url": "",
        "expose_real_path": True,
        "thumbnail_dir": ".tmb",
    }
    return settings
