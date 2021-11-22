#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

from sap.config import Config
import os
import pytest
from file_names import DATABASE_NAME, PUBLIC_KEY_NAME, PRIVATE_KEY_NAME


@pytest.fixture
def config(tmpdir):
    cfg = Config(tmpdir)
    cfg.create()
    yield cfg
    cfg.remove_config()


def test_config_create(config):
    assert True == os.path.exists(config.config_file_path)


def test_config_read(config, tmpdir):
    info = config.read()
    assert (info.db_type == 'sqlite') and (info.language == 'RU') and (
            info.db_path == os.path.join(tmpdir, DATABASE_NAME)) and (
                   info.private_key_path == os.path.join(tmpdir, PRIVATE_KEY_NAME)) and (
                   info.public_key_path == os.path.join(tmpdir, PUBLIC_KEY_NAME))
