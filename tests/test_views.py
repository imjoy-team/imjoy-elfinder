"""Test views."""
from imjoy_elfinder.views import connector, index


def test_index_view(p_config, p_request):
    """Test the index view."""
    response = index(p_request)

    assert response == {}


def test_connector_200(p_request, settings):
    """Test the connector view returns 200 response status code."""
    response = connector(p_request)

    assert response.status_code == 200
