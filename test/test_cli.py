#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import pytest
from click.testing import CliRunner
from sap.cli import run, list_systems, add, delete, debug, update
from sap.database import SapDB


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def database(tmpdir):
    path = tmpdir.join('sap_db.db')
    return SapDB(db_path=path, db_type='')


@pytest.fixture
def db(database, tmpdir):
    database.create()
    yield database
    database.stop_sap_db()
    database.drop()


# def test_run(runner):
#     result = runner.invoke(run, "dhv 100")
#     assert result.output == ('\n''\n''+------------------------------------------------------------+\n'
#                              '|           Trying to LAUNCH the following system            |\n'
#                              '+-------------+--------+---------+-------------+-------------+\n'
#                              '| Customer    | System | Mandant | Description | User        |\n'
#                              '+-------------+--------+---------+-------------+-------------+\n'
#                              '| BelarusNeft | DHV    | 100     | Dev         | DEVELOPER25 |\n'
#                              '+-------------+--------+---------+-------------+-------------+\n')


def test_list(runner):
    result = runner.invoke(list_systems, "dhv 100")
    assert result.output == ('\n''\n''+------------------------------------------------------------+\n'
                             '|                     Available systems                      |\n'
                             '+-------------+--------+---------+-------------+-------------+\n'
                             '| Customer    | System | Mandant | Description | User        |\n'
                             '+-------------+--------+---------+-------------+-------------+\n'
                             '| BelarusNeft | DHV    | 100     | Dev         | DEVELOPER25 |\n'
                             '+-------------+--------+---------+-------------+-------------+\n')


def test_add(runner):
    result = runner.invoke(add, input="XXX 100 Rygor 12345678 12345678 AK Test")
    result = run.invoke(list_systems, "XXX 100")
    assert result.output == ('\n''\n''+------------------------------------------------------------+\n'
                             '|                     Available systems                      |\n'
                             '+-------------+--------+---------+-------------+-------------+\n'
                             '| Customer    | System | Mandant | Description | User        |\n'
                             '+-------------+--------+---------+-------------+-------------+\n'
                             '| AK          | XXX    | 100     | Test        | Rygor       |\n'
                             '+-------------+--------+---------+-------------+-------------+\n')
