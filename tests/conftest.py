#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" General Fixtures """

from pathlib import Path
import pytest
from click.testing import CliRunner

from sap.api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, DEBUG_FILE_NAME
from sap.api import COMMAND_LINE_NAME, SAPLOGON_NAME, TEXT_FILE_NAME
from sap.cli import sap_cli
from sap.config import Config
from sap.crypto import Crypto
from sap.backup import Backup


@pytest.fixture(scope='session')
def runner():
    """ CliRunner """
    return CliRunner()


@pytest.fixture(scope='session')
def temp_start_cli(tmpdir_factory, runner):
    """
    Create temporary files (database, config, encryption keys)
    :param tmpdir_factory: factory to get base testing folder
    :param runner: click runner to run sap_cli commands
    """

    test_path = tmpdir_factory.getbasetemp()

    runner.invoke(sap_cli, args=['--config_path', test_path, "start", "-skip_message"])
    yield test_path
    Path(test_path / CONFIG_NAME).unlink()
    Path(test_path / PUBLIC_KEY_NAME).unlink()
    Path(test_path / PRIVATE_KEY_NAME).unlink()
    debug_file = Path(test_path / DEBUG_FILE_NAME)
    if debug_file.exists():
        debug_file.unlink()
    Path(test_path / DATABASE_NAME).unlink()


@pytest.fixture
def config_tmp_path(tmp_path):
    """ Create specific config with tmp_dir """
    cfg = Config(config_path=tmp_path)
    cfg.db_path = Path(tmp_path / DATABASE_NAME)
    cfg.db_type = "sqlite"
    cfg.command_line_path = Path(tmp_path / COMMAND_LINE_NAME)
    cfg.saplogon_path = Path(tmp_path / SAPLOGON_NAME)
    cfg.public_key_path = Path(tmp_path / PUBLIC_KEY_NAME)
    cfg.private_key_path = Path(tmp_path / PRIVATE_KEY_NAME)
    cfg.language = 'RU'
    cfg.create()
    yield cfg
    cfg.remove_config()


@pytest.fixture
def temp_crypto(tmp_path):
    """
    Create public and private encryption keys
    """
    public = Path(tmp_path / PUBLIC_KEY_NAME)
    private = Path(tmp_path / PRIVATE_KEY_NAME)
    crypto = Crypto(public, private)
    yield crypto
    crypto.remove_keys()


@pytest.fixture
def temp_backup_api(tmp_path):
    """
    Temporary backup creation with api
    """
    text_file_path = tmp_path / TEXT_FILE_NAME
    with text_file_path.open("w", encoding="UTF-8") as file:
        file.write("For backup")

    backup = Backup('12345678', tmp_path, [text_file_path])
    backup_path = backup.create()
    yield backup_path
    backup.delete()
    text_file_path.unlink()


@pytest.fixture
def temp_backup_cli(runner, tmp_path):
    """
    Temporary backup creation with command 'sap backup' from command line
    Temporary files (database, config, encryption keys)
    """
    runner.invoke(sap_cli, args=['--config_path', tmp_path, "start", "-skip_message"])
    result = runner.invoke(sap_cli,
                           args=['--config_path', tmp_path, "backup", "-password", "12345678", "-skip_message"])
    yield result
    Path(result.output.strip()).unlink()
    Path(tmp_path / DATABASE_NAME).unlink()
    Path(tmp_path / CONFIG_NAME).unlink()
    Path(tmp_path / PUBLIC_KEY_NAME).unlink()
    Path(tmp_path / PRIVATE_KEY_NAME).unlink()
