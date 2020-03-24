"""Test elfinder."""
import subprocess
from contextlib import ExitStack as default_context
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

# pylint: disable=too-many-arguments


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


@pytest.fixture(name="hashed_files")
def hashed_files_fixture(txt_file):
    """Return a dict of different hashed files."""
    return {
        "txt_file": make_hash(str(txt_file)),
        "txt_file_parent": make_hash(str(txt_file.parent)),
    }


def update_params(p_request, params, hashed_files):
    """Return a mock request with updated params."""
    params = {key: hashed_files.get(val, val) for key, val in params.items() if val}
    p_request.params.update(params)
    return p_request


@pytest.mark.parametrize(
    "error, api, in_body, init, target, tree, access",
    [
        (
            None,  # error
            None,  # api
            [
                R_CWD,
                R_NETDRIVERS,
                R_FILES,
                R_UPLMAXFILE,
                R_UPLMAXSIZE,
                R_OPTIONS,
            ],  # in_body
            None,  # init
            "txt_file_parent",  # target
            None,  # tree
            None,  # access
        ),  # With target and no init
        (
            None,
            2.1,
            [R_CWD, R_NETDRIVERS, R_FILES, R_UPLMAXFILE, R_UPLMAXSIZE, R_OPTIONS],
            True,
            None,
            True,
            None,
        ),  # With init, tree and no target
        (
            None,
            2.1,
            [R_CWD, R_NETDRIVERS, R_FILES, R_UPLMAXFILE, R_UPLMAXSIZE, R_OPTIONS],
            True,
            "txt_file_parent",
            None,
            None,
        ),  # With init and target
        (
            None,
            2.1,
            [R_CWD, R_NETDRIVERS, R_FILES, R_UPLMAXFILE, R_UPLMAXSIZE, R_OPTIONS],
            True,
            "missing",
            None,
            None,
        ),  # With init and missing target file
        (
            "Access denied",
            2.1,
            [],
            True,
            "txt_file_parent",
            None,
            {"file": "txt_file_parent", "mode": 0o100},
        ),  # With init and no read access to target
        (
            "Access denied",
            None,
            [],
            None,
            "txt_file_parent",
            None,
            {"file": "txt_file_parent", "mode": 0o100},
        ),  # With no init and no read access to target
        ("Invalid parameters", None, [], None, None, None, None,),
        ("File not found", None, [], None, "missing", None, None,),
    ],
    indirect=["access"],
)
def test_open(error, api, in_body, init, target, tree, access, p_request, hashed_files):
    """Test the open command."""
    params = {API_INIT: init, API_TARGET: target, API_TREE: tree}
    p_request = update_params(p_request, params, hashed_files)
    p_request.params[API_CMD] = "open"

    response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    for item in in_body:
        assert item in body
    assert body.get(R_ERROR) == error
    assert body.get(R_API) == api


@pytest.mark.parametrize(
    "error, added, type_, target, targets, access, context",
    [
        (
            None,  # error
            True,  # added
            "application/x-tar",  # type
            "txt_file_parent",  # target
            "txt_file",  # targets
            None,  # access
            default_context(),  # context
        ),  # Archive success
        ("Invalid parameters", False, None, None, None, None, default_context()),
        (
            "Invalid parameters",
            False,
            "application/x-tar",
            None,
            None,
            None,
            default_context(),
        ),  # Missing parameters target and targets
        (
            "Invalid parameters",
            False,
            "application/x-tar",
            "txt_file_parent",
            None,
            None,
            default_context(),
        ),  # Missing parameter targets
        (
            "Invalid parameters",
            False,
            "application/x-tar",
            None,
            "txt_file",
            None,
            default_context(),
        ),  # Missing parameter target
        (
            "Invalid parameters",
            False,
            None,
            "txt_file_parent",
            "txt_file",
            None,
            default_context(),
        ),  # Missing parameter type
        (
            "Unable to create archive",
            False,
            "missing",
            "txt_file_parent",
            "txt_file",
            None,
            default_context(),
        ),  # Incorrect archive type
        (
            "File not found",
            False,
            "application/x-tar",
            "missing",
            "txt_file",
            None,
            default_context(),
        ),  # Bad target directory
        (
            "File not found",
            False,
            "application/x-tar",
            "txt_file_parent",
            "missing",
            None,
            default_context(),
        ),  # Bad target file
        (
            "Access denied",
            False,
            "application/x-tar",
            "txt_file_parent",
            "txt_file",
            {"file": "txt_file_parent", "mode": 0o500},
            default_context(),
        ),  # Access denied
        (
            "Unable to create archive",
            False,
            "application/x-tar",
            "txt_file_parent",
            "txt_file",
            None,
            patch("subprocess.run", side_effect=OSError("Boom")),
        ),  # Archive action fails
    ],
    indirect=["access"],
)
def test_archive(
    error, added, type_, target, targets, access, context, p_request, all_params
):
    """Test the archive command."""
    params = {API_TYPE: type_, API_TARGET: target, API_TARGETS: targets}
    params = {key: val for key, val in params.items() if val}
    p_request.params[API_CMD] = "archive"
    p_request = update_params(p_request, params, all_params)

    with context:
        response = connector(p_request)

    assert response.status_code == 200
    body = response.json
    assert body.get(R_ERROR) == error
    assert (R_ADDED in body) is added


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
