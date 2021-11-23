#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Test of config.ini file """

import os
import pytest

from file_names import DATABASE_NAME, PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, COMMAND_LINE_PATH, SAPLOGON_PATH
from sap.config import Config


@pytest.fixture
def config_tmp_path(tmp_path):
    """ Create specific config with tmp_dir """
    cfg = Config(config_path=tmp_path,
                 db_path=os.path.join(tmp_path, DATABASE_NAME),
                 db_type='sqlite',
                 command_line_path=os.path.join(tmp_path, COMMAND_LINE_PATH),
                 saplogon_path=os.path.join(tmp_path, SAPLOGON_PATH),
                 public_key_path=os.path.join(tmp_path, PUBLIC_KEY_NAME),
                 private_key_path=os.path.join(tmp_path, PRIVATE_KEY_NAME),
                 language='RU')
    cfg.create()
    yield cfg
    cfg.remove_config()


def test_config_create(config_tmp_path):
    """ Check if config file is created """
    assert os.path.exists(config_tmp_path.config_file_path) is True


def test_read_tmp_path_config(config_tmp_path):
    """ Check values of config file"""
    info = config_tmp_path.read()
    assert (info.db_type == config_tmp_path.db_type) and (
            info.db_path == config_tmp_path.db_path) and (
                   info.private_key_path == config_tmp_path.private_key_path) and (
                   info.public_key_path == config_tmp_path.public_key_path) and (
                   info.command_line_path == config_tmp_path.command_line_path) and (
                   info.saplogon_path == config_tmp_path.saplogon_path) and (
                   info.language == 'RU')


@pytest.fixture
def config_default_path(tmp_path):
    """ Create config filc with tmp_path and default values """
    cfg = Config(config_path=tmp_path)
    cfg.create()
    yield cfg
    cfg.remove_config()


def test_read_default_config(config_default_path, tmp_path):
    """ Check values of config file with default values """
    info = config_default_path.read()
    assert (info.db_type == 'sqlite') and (
            info.db_path == os.path.join(tmp_path, DATABASE_NAME)) and (
                   info.private_key_path == os.path.join(tmp_path, PRIVATE_KEY_NAME)) and (
                   info.public_key_path == os.path.join(tmp_path, PUBLIC_KEY_NAME)) and (
                   info.command_line_path == 'path to sapshcut.exe file') and (
                   info.saplogon_path == 'path to saplogon.exe file') and (
                   info.language == 'RU')
