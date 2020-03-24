"""Test elfinder."""
import subprocess
from unittest.mock import patch

import pytest

from jupyter_elfinder.api_const import (
    API_CMD,
    API_INIT,
    API_MAKEDIR,
    API_TARGET,
    API_TARGETS,
    API_TREE,
    API_TYPE,
    R_ADDED,
    R_API,
    R_CWD,
    R_DIM,
    R_ERROR,
    R_FILES,
    R_NETDRIVERS,
    R_OPTIONS,
    R_UPLMAXFILE,
    R_UPLMAXSIZE,
)
from jupyter_elfinder.elfinder import make_hash
from jupyter_elfinder.views import connector


@pytest.fixture(name="all_files")
def all_files_fixture(txt_file, jpeg_file, zip_file):
    """Return a dict of different fixture file cases."""
    return {
        "txt_file": txt_file,
        "txt_file_parent": txt_file.parent,
        "jpeg_file": jpeg_file,
        "zip_file": zip_file,
    }


@pytest.fixture(name="access")
def access_fixture(all_files, request):
    """Set file access mode on selected pathlib file path."""
    settings = request.param
    if not settings:
        mode = 0o700
        fixture_file = all_files["txt_file_parent"]
    else:
        mode = settings["mode"]
        file_setting = settings["file"]
        fixture_file = all_files[file_setting]

    fixture_file.chmod(mode)
    yield
    fixture_file.chmod(0o700)  # Reset permissions


@pytest.fixture(name="all_params")
def all_params_fixture(txt_file):
    """Return a dict of different request param cases."""
    return {
        "missing": "missing",
        "txt_file": make_hash(str(txt_file)),
        "txt_file_parent": make_hash(str(txt_file.parent)),
        "true": True,
    }


@pytest.fixture(name="set_request")
def set_request_fixture(all_params, p_request, request):
    """Return a mock request with set params."""
    params = request.param
    params = {key: all_params[val] for key, val in params.items()}
    p_request.params.update(params)
    return p_request


def assert_response(response, body_items, in_body, not_in_body):
    """Assert the response."""
    assert response.status_code == 200
    body = response.json
    for key, val in body_items.items():
        assert body[key] == val
    for item in in_body:
        assert item in body
    for item in not_in_body:
        assert item not in body


@pytest.mark.parametrize(
    "body_items, in_body, not_in_body, set_request, access",
    [
        (
            {},
            [R_CWD, R_NETDRIVERS, R_FILES, R_UPLMAXFILE, R_UPLMAXSIZE, R_OPTIONS],
            [R_ERROR],
            {API_TARGET: "txt_file_parent"},
            None,
        ),  # With target and no init
        (
            {R_API: 2.1},
            [R_CWD, R_NETDRIVERS, R_FILES, R_UPLMAXFILE, R_UPLMAXSIZE, R_OPTIONS],
            [R_ERROR],
            {API_INIT: "true", API_TREE: "true"},
            None,
        ),  # With init and no target
        (
            {R_API: 2.1},
            [R_CWD, R_NETDRIVERS, R_FILES, R_UPLMAXFILE, R_UPLMAXSIZE, R_OPTIONS],
            [R_ERROR],
            {API_INIT: "true", API_TARGET: "txt_file_parent"},
            None,
        ),  # With init and target
        (
            {R_API: 2.1},
            [R_CWD, R_NETDRIVERS, R_FILES, R_UPLMAXFILE, R_UPLMAXSIZE, R_OPTIONS],
            [R_ERROR],
            {API_INIT: "true", API_TARGET: "missing"},
            None,
        ),  # With init and missing target
        (
            {R_ERROR: "Access denied"},
            [],
            [],
            {API_INIT: "true", API_TARGET: "txt_file_parent"},
            {"file": "txt_file_parent", "mode": 0o100},
        ),  # With init and no read access to target
    ],
    indirect=["set_request", "access"],
)
def test_open(body_items, in_body, not_in_body, set_request, access):
    """Test the open command."""
    set_request.params[API_CMD] = "open"

    response = connector(set_request)

    assert_response(response, body_items, in_body, not_in_body)


def test_open_errors(p_request, settings, txt_file):
    """Test the open command with errors."""
    # Invalid parameters
    p_request.params[API_CMD] = "open"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Invalid parameters"

    # File not found
    p_request.params.clear()
    p_request.params[API_CMD] = "open"
    p_request.params[API_TARGET] = "missing"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "File not found"

    # Access denied
    txt_file.parent.chmod(0o100)
    p_request.params.clear()
    p_request.params[API_CMD] = "open"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Access denied"
    txt_file.parent.chmod(0o600)  # Reset permissions


def test_archive(p_request, settings, txt_file):
    """Test the archive command."""
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR not in body
    assert "added" in body


def test_archive_errors(p_request, settings, txt_file):
    """Test the archive command with errors."""
    # Invalid parameters
    p_request.params[API_CMD] = "archive"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    # Incorrect archive type
    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "missing"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    # Bad target directory
    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    p_request.params[API_TARGET] = make_hash(str("missing"))
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    # Bad target file
    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    p_request.params[API_TARGETS] = make_hash(str(txt_file.parent / "missing"))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR in body

    # Access denied
    txt_file.parent.chmod(0o500)  # Set read and execute permission only
    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Access denied"

    txt_file.parent.chmod(0o700)  # Reset permissions

    # archive action fails
    p_request.params.clear()
    p_request.params[API_CMD] = "archive"
    p_request.params[API_TYPE] = "application/x-tar"
    p_request.params[API_TARGET] = make_hash(str(txt_file.parent))
    p_request.params[API_TARGETS] = make_hash(str(txt_file))

    with patch("subprocess.run", side_effect=OSError("Boom")):
        response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Unable to create archive"


def test_dim(p_request, settings, jpeg_file):
    """Test the dim command."""
    p_request.params[API_CMD] = "dim"
    # "substitute" is not supported in our backend yet. It's optional in api 2.1
    # p_request.params[API_SUBSTITUTE] = "640x480"
    p_request.params[API_TARGET] = make_hash(str(jpeg_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR not in body
    assert body[R_DIM] == "420x420"


def test_dim_errors(p_request, settings, jpeg_file):
    """Test the dim command with errors."""
    # Invalid parameters
    p_request.params[API_CMD] = "dim"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Invalid parameters"

    # File not found
    p_request.params.clear()
    p_request.params[API_CMD] = "dim"
    p_request.params[API_TARGET] = make_hash(str("missing"))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "File not found"

    # Access denied
    jpeg_file.chmod(0o100)  # Set execute permission only
    p_request.params.clear()
    p_request.params[API_CMD] = "dim"
    p_request.params[API_TARGET] = make_hash(str(jpeg_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Access denied"

    # TODO: Add a test if the image library cannot calculate dimensions.
    # Change the code to return an error in the response first.


def test_duplicate(p_request, settings, txt_file):
    """Test the duplicate command."""
    ext = txt_file.suffix
    duplicated_file = "{} copy{}".format(txt_file.stem, ext)
    duplicated_path = txt_file.parent / duplicated_file
    p_request.params[API_CMD] = "duplicate"
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR not in body
    assert R_ADDED in body
    assert body[R_ADDED][0]["hash"] == make_hash(str(duplicated_path))


def test_duplicate_errors(p_request, settings, txt_file):
    """Test the duplicate command with errors."""
    # Invalid parameters
    p_request.params[API_CMD] = "duplicate"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Invalid parameters"

    # File not found
    p_request.params.clear()
    p_request.params[API_CMD] = "duplicate"
    p_request.params[API_TARGETS] = make_hash(str("missing"))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "File not found"

    # Access denied
    txt_file.chmod(0o100)  # Set execute permission only
    p_request.params.clear()
    p_request.params[API_CMD] = "duplicate"
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Access denied"

    txt_file.chmod(0o600)  # Reset permissions

    current = txt_file.parent
    current.chmod(0o500)  # Set read and execute permission only
    p_request.params.clear()
    p_request.params[API_CMD] = "duplicate"
    p_request.params[API_TARGETS] = make_hash(str(txt_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Access denied"

    current.chmod(0o700)  # Reset permissions

    # duplicate action fails
    p_request.params.clear()
    p_request.params[API_CMD] = "duplicate"
    p_request.params[API_TARGETS] = make_hash(str(txt_file))

    with patch("shutil.copyfile", side_effect=OSError("Boom")):
        response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Unable to create file copy"


def test_extract(p_request, settings, zip_file):
    """Test the extract command."""
    extracted_file = zip_file.parent / "{}.txt".format(zip_file.stem)
    p_request.params[API_CMD] = "extract"
    p_request.params[API_TARGET] = make_hash(str(zip_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR not in body
    assert R_ADDED in body
    assert body[R_ADDED][0]["hash"] == make_hash(str(extracted_file))

    new_dir = zip_file.parent / zip_file.stem
    p_request.params[API_MAKEDIR] = "1"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert R_ERROR not in body
    assert R_ADDED in body
    assert body[R_ADDED][0]["hash"] == make_hash(str(new_dir))


def test_extract_errors(p_request, settings, zip_file):
    """Test the extract command with errors."""
    # Invalid parameters
    p_request.params[API_CMD] = "extract"
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Invalid parameters"

    # File not found
    p_request.params.clear()
    p_request.params[API_CMD] = "extract"
    p_request.params[API_TARGET] = make_hash(str("missing"))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "File not found"

    p_request.params.clear()
    p_request.params[API_CMD] = "extract"
    p_request.params[API_TARGET] = make_hash(str(zip_file.parent))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "File not found"

    # Access denied
    current = zip_file.parent
    current.chmod(0o500)  # Set read and execute permission only
    p_request.params.clear()
    p_request.params[API_CMD] = "extract"
    p_request.params[API_TARGET] = make_hash(str(zip_file))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Access denied"
    current.chmod(0o700)  # Reset permissions

    # Bad mime type
    bad_mime = zip_file.parent / "{}.bad".format(zip_file.stem)
    zip_file.rename(bad_mime)
    p_request.params.clear()
    p_request.params[API_CMD] = "extract"
    p_request.params[API_TARGET] = make_hash(str(bad_mime))
    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Unable to extract files from archive"
    bad_mime.rename(zip_file)  # Reset file name

    # mkdir fails
    p_request.params.clear()
    p_request.params[API_CMD] = "extract"
    p_request.params[API_TARGET] = make_hash(str(zip_file))
    p_request.params[API_MAKEDIR] = "1"
    with patch("os.mkdir", side_effect=OSError("Boom")):
        response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Unable to create folder: {}".format(zip_file.stem)

    # unzip fails
    p_request.params.clear()
    p_request.params[API_CMD] = "extract"
    p_request.params[API_TARGET] = make_hash(str(zip_file))

    programs = set()
    orig_subprocess_run = subprocess.run

    def mock_subprocess_run(args, **kwargs):
        """Raise the second time a program is called."""
        prog = args[0]
        if prog in programs:
            raise OSError("Boom")
        programs.add(prog)
        return orig_subprocess_run(  # pylint: disable=subprocess-run-check
            args, **kwargs
        )

    with patch("subprocess.run", side_effect=mock_subprocess_run):
        response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body[R_ERROR] == "Unable to extract files from archive"
