"""Provide pytest fixtures.."""
import shutil

import pytest
from pyramid import testing

from . import ROOT_PATH, TEST_CONTENT, ZIP_FILE


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
    thumbs_dir = ".tmb"
    settings = {
        "root_dir": str(tmp_path),
        "files_url": "/files",
        "base_url": "",
        "expose_real_path": True,
        "dot_files": False,
        "thumbnail_dir": thumbs_dir,
    }
    thumbs_dir = tmp_path / thumbs_dir
    thumbs_dir.mkdir(exist_ok=True)
    return settings


@pytest.fixture(name="txt_file")
def txt_file_fixture(tmp_path):
    """Provide a temporary text file."""
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir(exist_ok=True)
    fil = tmp_dir / "test.txt"
    fil.write_text(TEST_CONTENT)
    yield fil


@pytest.fixture(name="link_txt_file")
def link_txt_file_fixture(tmp_path):
    """Provide a link to a temporary text file."""
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir(exist_ok=True)
    fil = tmp_dir / "test.txt"
    fil.write_text(TEST_CONTENT)
    link_tmp_dir = tmp_path / "link_sub"
    link_tmp_dir.mkdir(exist_ok=True)
    link = link_tmp_dir / "link_text"
    link.symlink_to(fil)
    yield link


@pytest.fixture(name="link_dir")
def link_dir_fixture(tmp_path):
    """Provide a link to a temporary directory."""
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir(exist_ok=True)
    link = tmp_path / "link_dir"
    link.symlink_to(tmp_dir)
    yield link


@pytest.fixture(name="bad_link")
def bad_link_fixture(tmp_path):
    """Provide a link to a missing target file."""
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir(exist_ok=True)
    fil = tmp_dir / "bad_target.txt"
    fil.write_text(TEST_CONTENT)
    link = tmp_dir / "bad_link"
    link.symlink_to(fil)
    fil.unlink()
    yield link


@pytest.fixture(name="jpeg_file")
def jpeg_file_fixture(tmp_path):
    """Provide a temporary jpeg file."""
    fly_img = ROOT_PATH / "example-data" / "fly.jpeg"
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir(exist_ok=True)
    test_fil = tmp_dir / "test.jpeg"
    # Python 3.5 shutil.copyfile needs strings instead of pathlib paths
    shutil.copyfile(str(fly_img), str(test_fil))
    yield test_fil


@pytest.fixture(name="zip_file")
def zip_file_fixture(tmp_path):
    """Provide a temporary zip file."""
    foo_zip = ROOT_PATH / "example-data" / "test" / ZIP_FILE
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir(exist_ok=True)
    test_fil = tmp_dir / ZIP_FILE
    # Python 3.5 shutil.copyfile needs strings instead of pathlib paths
    shutil.copyfile(str(foo_zip), str(test_fil))
    yield test_fil
