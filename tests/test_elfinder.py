"""Test elfinder."""
import subprocess
from contextlib import ExitStack as default_context
from pathlib import Path
from unittest.mock import patch

import pytest

from imjoy_elfinder.api_const import (
    API_CMD,
    API_CONTENT,
    API_DOWNLOAD,
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
from imjoy_elfinder.elfinder import make_hash

from . import ZIP_FILE, ZIP_FILE_ASCII_CONTENT

# pylint: disable=too-many-arguments


@pytest.fixture(name="all_files")
def all_files_fixture(
    bad_link, link_dir, link_txt_file, tmp_path, txt_file, jpeg_file, zip_file
):
    """Return a dict of different fixture file cases."""
    return {
        "bad_link": bad_link,
        "link_dir": link_dir,
        "link_txt_file": link_txt_file,
        "tmp_path": tmp_path,
        "txt_file": txt_file,
        "txt_file_parent": txt_file.parent,
        "jpeg_file": jpeg_file,
        "zip_file": zip_file,
        "zip_file_parent": zip_file.parent,
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
def hashed_files_fixture(
    bad_link, link_dir, link_txt_file, tmp_path, txt_file, jpeg_file, zip_file
):
    """Return a dict of different hashed files."""
    return {
        "bad_link": make_hash(str(bad_link)),
        "link_dir": make_hash(str(link_dir)),
        "link_txt_file": make_hash(str(link_txt_file)),
        "tmp_path": make_hash(str(tmp_path)),
        "txt_file": make_hash(str(txt_file)),
        "txt_file_parent": make_hash(str(txt_file.parent)),
        "jpeg_file": make_hash(str(jpeg_file)),
        "zip_file": make_hash(str(zip_file)),
        "zip_file_parent": make_hash(str(zip_file.parent)),
    }


def update_params(request_params, params, hashed_files):
    """Return a mock request with updated params."""
    params = {key: hashed_files.get(val, val) for key, val in params.items() if val}
    request_params.params.update(params)
    return request_params


def update_settings(settings, updates, files):
    """Return updated settings."""
    updates = {key: str(files.get(val, val)) for key, val in updates.items()}
    for attr, value in updates.items():
        setattr(settings, attr, value)

    return settings


def raise_subprocess_after_check_archivers():
    """Return a mock subprocess.run function."""
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

    return mock_subprocess_run


@pytest.mark.parametrize(
    "error, root, command, access, context",
    [
        (
            "Invalid backend configuration",  # error
            "missing",  # root
            "ping",  # command
            None,  # access
            default_context(),  # context
        ),  # Root dir does not exist
        (
            "Access denied",
            "tmp_path",
            "ping",
            {"file": "tmp_path", "mode": 0o100},
            default_context(),
        ),  # Access denied
        (
            "Command Failed: ping, Error: \nBoom",
            "tmp_path",
            "ping",
            None,
            patch(
                "imjoy_elfinder.elfinder.Connector._Connector__ping",
                side_effect=RuntimeError("Boom"),
            ),
        ),  # Action raises uncaught exception
        (
            "Unknown command: missing",
            "tmp_path",
            "missing",
            None,
            default_context(),
        ),  # Unknown command
    ],
    indirect=["access"],
)
def test_run(
    settings,
    error,
    root,
    command,
    access,
    context,
    client,
    request_params,
    all_files,
):
    """Test the run method."""
    request_params.params[API_CMD] = command
    updates = {"root_dir": root, "thumbnail_dir": ""}
    settings = update_settings(settings, updates, all_files)

    with context:
        response = client.post("/connector", params=request_params.params)

    assert response.status_code == 200
    body = response.json()
    assert body.get(R_ERROR) == error


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
        (
            "Invalid parameters",
            None,
            [],
            None,
            None,
            None,
            None,
        ),
        (
            "File not found",
            None,
            [],
            None,
            "missing",
            None,
            None,
        ),
    ],
    indirect=["access"],
)
def test_open(
    error,
    api,
    in_body,
    init,
    target,
    tree,
    access,
    client,
    request_params,
    hashed_files,
):
    """Test the open command."""
    request_params.params[API_CMD] = "open"
    params = {API_INIT: init, API_TARGET: target, API_TREE: tree}
    request_params = update_params(request_params, params, hashed_files)

    response = client.post("/connector", params=request_params.params)

    assert response.status_code == 200
    body = response.json()
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
    error,
    added,
    type_,
    target,
    targets,
    access,
    context,
    client,
    request_params,
    hashed_files,
):
    """Test the archive command."""
    request_params.params[API_CMD] = "archive"
    params = {API_TYPE: type_, API_TARGET: target, API_TARGETS: targets}
    request_params = update_params(request_params, params, hashed_files)

    with context:
        response = client.post("/connector", params=request_params.params)

    assert response.status_code == 200
    body = response.json()
    assert body.get(R_ERROR) == error
    assert (R_ADDED in body) is added


@pytest.mark.parametrize(
    "error, dim, target, access, context",
    [
        (
            None,  # error
            "420x420",  # dim
            "jpeg_file",  # target
            None,  # access
            default_context(),  # context
        ),  # Dim success
        (
            "Invalid parameters",
            None,
            None,
            None,
            default_context(),
        ),  # Missing parameter target
        (
            "File not found",
            None,
            "missing",
            None,
            default_context(),
        ),  # Bad target file
        (
            "Access denied",
            None,
            "jpeg_file",
            {"file": "jpeg_file", "mode": 0o100},
            default_context(),
        ),  # Access denied
        (
            None,
            None,
            "jpeg_file",
            None,
            patch("PIL.Image.open", side_effect=OSError("Boom")),
        ),  # Dim action fails
    ],
    indirect=["access"],
)
def test_dim(error, dim, target, access, context, client, request_params, hashed_files):
    """Test the dim command."""
    # "substitute" is not supported in our backend yet. It's optional in api 2.1
    # request_params.params[API_SUBSTITUTE] = "640x480"
    request_params.params[API_CMD] = "dim"
    params = {API_TARGET: target}
    request_params = update_params(request_params, params, hashed_files)

    with context:
        response = client.post("/connector", params=request_params.params)

    assert response.status_code == 200
    body = response.json()
    assert body.get(R_ERROR) == error
    assert body.get(R_DIM) == dim


@pytest.mark.parametrize(
    "error, added, targets, access, context",
    [
        (
            None,  # error
            True,  # added
            "txt_file",  # targets
            None,  # access
            default_context(),  # context
        ),  # Duplicate success
        (
            "Invalid parameters",
            False,
            None,
            None,
            default_context(),
        ),  # Missing parameter targets
        (
            "File not found",
            False,
            "missing",
            None,
            default_context(),
        ),  # Bad target file
        (
            "Access denied",
            False,
            "txt_file",
            {"file": "txt_file", "mode": 0o100},
            default_context(),
        ),  # Access denied to target
        (
            "Access denied",
            False,
            "txt_file",
            {"file": "txt_file_parent", "mode": 0o500},
            default_context(),
        ),  # Access denied to parent
        (
            "Unable to create file copy",
            False,
            "txt_file",
            None,
            patch("shutil.copyfile", side_effect=OSError("Boom")),
        ),  # Duplicate action fails
    ],
    indirect=["access"],
)
def test_duplicate(
    error, added, targets, access, context, client, request_params, hashed_files
):
    """Test the duplicate command."""
    request_params.params[API_CMD] = "duplicate"
    params = {API_TARGETS: targets}
    request_params = update_params(request_params, params, hashed_files)

    with context:
        response = client.post(
            "/connector",
            params=request_params.params,
        )

    assert response.status_code == 200
    body = response.json()
    assert body.get(R_ERROR) == error
    assert (R_ADDED in body) is added


@pytest.mark.parametrize(
    "error, added, target, makedir, access, context",
    [
        (
            None,  # error
            True,  # added
            "zip_file",  # target
            None,  # makedir
            None,  # access
            default_context(),  # context
        ),  # Extract success
        (
            None,  # error
            True,  # added
            "zip_file",  # target
            "1",  # makedir
            None,  # access
            default_context(),  # context
        ),  # Extract success with makedir
        (
            "Invalid parameters",
            False,
            None,
            None,
            None,
            default_context(),
        ),  # Missing parameter target
        (
            "File not found",
            False,
            "missing",
            None,
            None,
            default_context(),
        ),  # Bad target directory
        (
            "File not found",
            False,
            "zip_file_parent",
            None,
            None,
            default_context(),
        ),  # Bad target file
        (
            "Unable to extract files from archive",
            False,
            "txt_file",
            None,
            None,
            default_context(),
        ),  # Incorrect archive type
        (
            "Access denied",
            False,
            "zip_file",
            None,
            {"file": "zip_file_parent", "mode": 0o500},
            default_context(),
        ),  # Access denied to write to parent dir
        (
            "File not found",
            False,
            "zip_file",
            None,
            {"file": "zip_file_parent", "mode": 0o300},
            default_context(),
        ),  # Access denied when listing parent files
        (
            f"Unable to create folder: {Path(ZIP_FILE).stem}",
            False,
            "zip_file",
            "1",
            None,
            patch("os.mkdir", side_effect=OSError("Boom")),
        ),
        (
            "Unable to extract files from archive",
            False,
            "zip_file",
            None,
            None,
            patch(
                "subprocess.run", side_effect=raise_subprocess_after_check_archivers()
            ),
        ),
    ],
    indirect=["access"],
)
def test_extract(
    error, added, target, makedir, access, context, client, request_params, hashed_files
):
    """Test the extract command."""
    request_params.params[API_CMD] = "extract"
    params = {API_TARGET: target, API_MAKEDIR: makedir}
    request_params = update_params(request_params, params, hashed_files)

    with context:
        response = client.post("/connector", params=request_params.params)

    assert response.status_code == 200
    body = response.json()
    assert body.get(R_ERROR) == error
    assert (R_ADDED in body) is added


@pytest.mark.parametrize(
    "text, status, content_type, content_disp, content_length, "
    "target, download, access, context",
    [
        (
            "test content",  # text
            200,  # status
            "text/plain",  # content_type
            "inline;",  # content_disp
            "12",  # content_length
            "txt_file",  # target
            None,  # download
            None,  # access
            default_context(),  # context
        ),  # file success
        (
            "test content",  # text
            200,  # status
            "text/plain",  # content_type
            "attachments;",  # content_disp
            "12",  # content_length
            "txt_file",  # target
            True,  # download
            None,  # access
            default_context(),  # context
        ),  # file success with download
        (
            None,  # text
            200,  # status
            "image/jpeg",  # content_type
            "image;",  # content_disp
            "22405",  # content_length
            "jpeg_file",  # target
            None,  # download
            None,  # access
            default_context(),  # context
        ),  # image file success
        (
            "test content",  # text
            200,  # status
            "text/plain",  # content_type
            "inline;",  # content_disp
            "12",  # content_length
            "link_txt_file",  # target
            None,  # download
            None,  # access
            default_context(),  # context
        ),  # link file success
        (
            "Invalid parameters",
            200,
            "text/html",  # content_type
            None,  # content_disp
            "18",
            None,
            None,
            None,
            default_context(),
        ),  # Missing all parameters
        (
            "Invalid parameters",
            200,
            "text/html",  # content_type
            None,  # content_disp
            "18",
            None,
            True,
            None,
            default_context(),
        ),  # Missing parameter target
        (
            "File not found",
            404,
            "text/html",  # content_type
            None,  # content_disp
            "14",
            "missing",
            None,
            None,
            default_context(),
        ),  # Bad target file
        (
            "File not found",
            404,
            "text/html",  # content_type
            None,  # content_disp
            "14",
            "bad_link",
            None,
            None,
            default_context(),
        ),  # Link and bad target file
        (
            "File not found",
            404,
            "text/html",  # content_type
            None,  # content_disp
            "14",
            "txt_file_parent",
            None,
            None,
            default_context(),
        ),  # Target is directory
        (
            "File not found",
            404,
            "text/html",  # content_type
            None,  # content_disp
            "14",
            "link_dir",
            None,
            None,
            default_context(),
        ),  # Link and target is directory
        (
            "Access denied",
            403,
            "text/html",  # content_type
            None,  # content_disp
            "13",
            "txt_file",
            None,
            {"file": "txt_file", "mode": 0o300},
            default_context(),
        ),  # Access denied
        (
            "Access denied",
            403,
            "text/html",  # content_type
            None,  # content_disp
            "13",
            "link_txt_file",
            None,
            {"file": "txt_file", "mode": 0o300},
            default_context(),
        ),  # Link and access denied
        (
            "File not found",
            404,
            "text/html",  # content_type
            None,  # content_disp
            "14",
            "txt_file",
            None,
            {"file": "txt_file_parent", "mode": 0o300},
            default_context(),
        ),  # Access denied for parent directory
        (
            "Access denied",
            403,
            "text/html",  # content_type
            None,  # content_disp
            "13",
            "link_txt_file",
            None,
            {"file": "txt_file_parent", "mode": 0o300},
            default_context(),
        ),  # Link and access denied for target parent directory
    ],
    indirect=["access"],
)
def test_file(
    text,
    status,
    content_type,
    content_disp,
    content_length,
    target,
    download,
    access,
    context,
    client,
    request_params,
    hashed_files,
):
    """Test the file command."""
    request_params.params[API_CMD] = "file"
    params = {API_TARGET: target, API_DOWNLOAD: download}
    request_params = update_params(request_params, params, hashed_files)

    with context:
        response = client.post("/connector", params=request_params.params)

    assert response.status_code == status
    assert response.headers["Content-type"] == content_type
    assert response.headers.get("Content-Disposition") == content_disp
    assert response.headers.get("Content-Length") == content_length
    if text is not None:
        assert response.text == text


@pytest.mark.parametrize(
    "error, content, target, access, context",
    [
        (
            None,  # error
            "test content",  # content
            "txt_file",  # target
            None,  # access
            default_context(),  # context
        ),  # Get success
        (
            None,  # error
            ZIP_FILE_ASCII_CONTENT,  # content
            "zip_file",  # target
            None,  # access
            default_context(),  # context
        ),  # Get success with binary file
        (
            "Invalid parameters",
            None,
            None,
            None,
            default_context(),
        ),  # Missing parameter target
        (
            "File not found",
            None,
            "missing",
            None,
            default_context(),
        ),  # Bad target file
        (
            "Access denied",
            None,
            "txt_file",
            {"file": "txt_file", "mode": 0o100},
            default_context(),
        ),  # Access denied
        (
            "File not found",
            None,
            "txt_file",
            {"file": "txt_file_parent", "mode": 0o100},
            default_context(),
        ),  # Access denied to parent diretory
    ],
    indirect=["access"],
)
def test_get(
    error, content, target, access, context, client, request_params, hashed_files
):
    """Test the get command."""
    request_params.params[API_CMD] = "get"
    params = {API_TARGET: target}
    request_params = update_params(request_params, params, hashed_files)

    with context:
        response = client.post("/connector", params=request_params.params)

    assert response.status_code == 200
    body = response.json()
    assert body.get(R_ERROR) == error
    assert body.get(API_CONTENT) == content
