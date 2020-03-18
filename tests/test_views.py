"""Test views."""
import pytest
from pyramid import testing

from jupyter_elfinder.views import index


@pytest.fixture(name="p_config")
def config_fixture():
    """Provide a mock pyramid Configurator instance.

    This also sets up and tearsdown the context before and after the test.
    """
    with testing.testConfig() as config:
        yield config


@pytest.fixture(name="p_request")
def request_fixture():
    """Provide a mock pyramid Request instance."""
    request = testing.DummyRequest()
    return request


def test_index_view(p_config, p_request):
    """Test the index view."""
    response = index(p_request)

    assert response == {}
