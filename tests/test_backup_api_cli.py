#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Backup Test """

from pathlib import Path
from zipfile import ZipFile

from sap.backup import Backup
from sap.api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, SAPLOGON_INI, TEXT_FILE_NAME


# API
def test_created_backup_file_api(temp_backup_api):
    """ Checking if backup is created"""
    assert temp_backup_api.exists()


def test_check_archived_files_api(temp_backup_api):
    """ Check files: only one file in archive and specific filename"""
    archive = ZipFile(temp_backup_api)
    assert len(archive.filelist) == 1 and archive.filelist[0].filename == TEXT_FILE_NAME


def test_archive_comment_api(temp_backup_api):
    """ Check archive comment """
    archive = ZipFile(temp_backup_api)
    assert archive.comment.decode() == Backup.comment


def test_created_backup_file_cli(temp_backup_cli):
    """ Checking if backup is created"""
    assert Path(temp_backup_cli.output.strip()).exists()


def test_check_archived_files_cli(temp_backup_cli):
    """ Check files: only one file in archive and specific filename"""
    archive = ZipFile(temp_backup_cli.output.strip())
    filenames = [PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, SAPLOGON_INI]
    filenames.sort()
    archived_files = []
    for item in archive.filelist:
        archived_files.append(item.filename)
    archived_files.sort()

    assert archived_files == filenames


def test_archive_comment_cli(temp_backup_cli):
    """ Check archive comment """
    archive = ZipFile(temp_backup_cli.output.strip())
    assert archive.comment.decode() == Backup.comment
