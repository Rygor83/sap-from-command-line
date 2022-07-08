#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Backup Test """

import os.path
from zipfile import ZipFile
import pytest
from click.testing import CliRunner

from sap.backup import Backup
from sap.cli import sap_cli
from sap.api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, SAPLOGON_INI

text_file_name = 'text_file.txt'


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_backup_api(tmp_path):
    """
    Temporary backup creation with api
    """
    text_file_path = os.path.join(tmp_path, text_file_name)
    with open(text_file_path, "w", encoding="UTF-8") as file:
        file.write("For backup")

    backup = Backup('12345678', tmp_path, [text_file_path])
    backup_path = backup.create()
    yield backup_path
    backup.delete()
    os.remove(text_file_path)


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
    os.remove(result.output.strip())
    os.remove(os.path.join(tmp_path, DATABASE_NAME))
    os.remove(os.path.join(tmp_path, CONFIG_NAME))
    os.remove(os.path.join(tmp_path, PUBLIC_KEY_NAME))
    os.remove(os.path.join(tmp_path, PRIVATE_KEY_NAME))


# API
def test_created_backup_file_api(temp_backup_api):
    """ Checking if backup is created"""
    assert os.path.exists(temp_backup_api) == True


def test_check_archived_files_api(temp_backup_api):
    """ Check files: only one file in archive and specific filename"""
    archive = ZipFile(temp_backup_api)
    assert len(archive.filelist) == 1 and archive.filelist[0].filename == text_file_name


def test_archive_comment_api(temp_backup_api):
    """ Check archive comment """
    archive = ZipFile(temp_backup_api)
    assert archive.comment.decode() == Backup.comment


# CLI

def test_created_backup_file_cli(temp_backup_cli):
    """ Checking if backup is created"""
    assert os.path.exists(temp_backup_cli.output.strip()) == True


def test_check_archived_files_cli(temp_backup_cli):
    """ Check files: only one file in archive and specific filename"""
    archive = ZipFile(temp_backup_cli.output.strip())
    filenames = [PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, SAPLOGON_INI]
    filenames.sort()
    archived_files = []
    for item in archive.filelist: archived_files.append(item.filename)
    archived_files.sort()

    assert archived_files == filenames


def test_archive_comment_cli(temp_backup_cli):
    """ Check archive comment """
    archive = ZipFile(temp_backup_cli.output.strip())
    assert archive.comment.decode() == Backup.comment
