#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Configuration file Tests """

from pathlib import Path
import pytest

from sap.api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, DATABASE_NAME
from sap.config import Config


def test_config_create(config_tmp_path):
    """ Check if config file is created """
    assert config_tmp_path.config_file_path.exists()


def test_read_tmp_path_config(config_tmp_path):
    """ Check values of config file"""
    info = config_tmp_path.read()
    assert (info.db_type == config_tmp_path.db_type) and (
            info.db_path == config_tmp_path.db_path) and (
                   info.private_key_path == config_tmp_path.private_key_path) and (
                   info.public_key_path == config_tmp_path.public_key_path) and (
                   info.command_line_path == config_tmp_path.command_line_path) and (
                   info.saplogon_path == config_tmp_path.saplogon_path) and (
                   info.language == 'RU') and (info.sequence == "{USER}{TAB}{PASS}{ENTER}") and (
                   info.wait_site_to_load == 4)


@pytest.fixture
def config_default_path(tmp_path):
    """ Create config file with tmp_path and default values """
    cfg = Config(config_path=tmp_path)
    cfg.create()
    yield cfg
    cfg.remove_config()


def test_read_default_config(config_default_path, tmp_path):
    """ Check values of config file with default values """
    info = config_default_path.read()
    assert (info.db_type == 'sqlite') and (
            info.db_path == tmp_path / DATABASE_NAME) and (
                   info.private_key_path == tmp_path / PRIVATE_KEY_NAME) and (
                   info.public_key_path == tmp_path / PUBLIC_KEY_NAME) and (
                   info.command_line_path == Path('path to sapshcut.exe file.')) and (
                   info.saplogon_path == Path('path to saplogon.exe file.')) and (
                   info.language == 'RU')
