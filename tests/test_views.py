"""Test views."""


def test_index_view(client):
    """Test the index view."""
    response = client.get("/")

    assert response.status_code == 200


def test_connector_200(client):
    """Test the connector view returns 200 response status code."""
    response = client.get("/connector")

    assert response.status_code == 200
