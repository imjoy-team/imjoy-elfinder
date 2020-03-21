"""Test elfinder."""
from jupyter_elfinder.elfinder import make_hash
from jupyter_elfinder.views import connector


def test_open(p_request, settings):
    """Test the open command."""
    p_request.params["cmd"] = "open"
    p_request.params["init"] = True
    p_request.params["tree"] = True
    p_request.params["target"] = None
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" not in body
    assert body["api"] >= 2.1
    assert "cwd" in body
    assert "netDrivers" in body
    # Part of api 2.1 but currently not implemented in our Python backend
    # assert "files" in body
    # Optional
    assert "uplMaxFile" in body
    assert "uplMaxSize" in body
    assert "options" in body


def test_archive(p_request, settings, txt_file):
    """Test the archive command."""
    p_request.params["cmd"] = "archive"
    p_request.params["type"] = "application/x-tar"
    p_request.params["target"] = make_hash(str(txt_file.parent))
    p_request.params["targets[]"] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" not in body
    assert "added" in body


def test_archive_error(p_request, settings, txt_file):
    """Test the archive command with error conditions."""
    # Missing parameters
    p_request.params["cmd"] = "archive"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body

    p_request.params.clear()
    p_request.params["cmd"] = "archive"
    p_request.params["type"] = "application/x-tar"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body

    p_request.params.clear()
    p_request.params["cmd"] = "archive"
    p_request.params["type"] = "application/x-tar"
    p_request.params["target"] = make_hash(str(txt_file.parent))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body

    p_request.params.clear()
    p_request.params["cmd"] = "archive"
    p_request.params["type"] = "application/x-tar"
    p_request.params["targets[]"] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body

    p_request.params.clear()
    p_request.params["cmd"] = "archive"
    p_request.params["target"] = make_hash(str(txt_file.parent))
    p_request.params["targets[]"] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body

    # Incorrect archive type
    p_request.params.clear()
    p_request.params["cmd"] = "archive"
    p_request.params["type"] = "missing"
    p_request.params["target"] = make_hash(str(txt_file.parent))
    p_request.params["targets[]"] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body

    # Bad target directory
    p_request.params.clear()
    p_request.params["cmd"] = "archive"
    p_request.params["type"] = "application/x-tar"
    p_request.params["target"] = make_hash(str("missing"))
    p_request.params["targets[]"] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body

    # Bad target file
    p_request.params.clear()
    p_request.params["cmd"] = "archive"
    p_request.params["type"] = "application/x-tar"
    p_request.params["target"] = make_hash(str(txt_file.parent))
    p_request.params["targets[]"] = make_hash(str(txt_file.parent / "missing"))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert "error" in body
