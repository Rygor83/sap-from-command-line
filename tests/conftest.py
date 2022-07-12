#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" General Fixtures """

import os
import pytest
from click.testing import CliRunner

from api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, DEBUG_FILE_NAME
from sap.cli import sap_cli


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
    os.remove(os.path.join(test_path, CONFIG_NAME))
    os.remove(os.path.join(test_path, PUBLIC_KEY_NAME))
    os.remove(os.path.join(test_path, PRIVATE_KEY_NAME))
    debug_file = os.path.join(test_path, DEBUG_FILE_NAME)
    if os.path.exists(debug_file):
        os.remove(debug_file)
    os.remove(os.path.join(test_path, DATABASE_NAME))
