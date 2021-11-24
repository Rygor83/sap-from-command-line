#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Test for Command Line """

import os
import pytest
import pyperclip

from click.testing import CliRunner
from sap.cli import sap_cli
from sap.database import SapDB
from sap.crypto import Crypto
from sap.api import Sap_system
from sap.config import Config
from sap.file_names import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME
from sap.file_names import COMMAND_LINE_PATH, SAPLOGON_PATH, DEBUG_FILE_NAME


########################################################################################################################
# Test with temporary created config, encrypt keys and database
########################################################################################################################

@pytest.fixture
def crypto(tmp_path):
    """ Prepare temporary encryption keys """
    crypt = Crypto(tmp_path.joinpath(PUBLIC_KEY_NAME), tmp_path.joinpath(PRIVATE_KEY_NAME))
    crypt.generate_keys()
    yield crypt
    crypt.remove_keys()


@pytest.fixture
def database(tmp_path):
    """ Prepare database with temporary path"""
    database_path = tmp_path.joinpath(DATABASE_NAME)
    return SapDB(db_path=database_path)


@pytest.fixture
def db(database):
    """ Prepare temporary database """
    database.create()
    yield database
    database.stop_sap_db()
    database.drop()


@pytest.fixture
def added_record(db, crypto):
    """ Add temporary record for testing purpose """
    sys_list = ['XXX', '100', 'USER', crypto.encrypto(str.encode('123')), 'CUSTOMER', 'DEV_SYSTEM']
    system = Sap_system(*sys_list)
    db.add(system)
    sys_list = ['YYY', '100', 'USER', crypto.encrypto(str.encode('123')), 'CUSTOMER', 'DEV_SYSTEM']
    system = Sap_system(*sys_list)
    db.add(system)
    return sys_list


@pytest.fixture
def config_tmp_path(tmp_path, db, crypto):
    """ Create specific config with tmp_dir """
    cfg = Config(config_path=tmp_path,
                 db_path=db.database_path,
                 db_type='sqlite',
                 public_key_path=crypto.public_key_path,
                 private_key_path=crypto.private_key_path,
                 language='RU')
    cfg.create()
    yield cfg
    cfg.remove_config()


@pytest.fixture
def runner():
    return CliRunner()


def test_list_added_system_outside_comman_line(runner, config_tmp_path, added_record):
    """ Test LIST command with records in temporary database created from api"""
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, "list", "xxx", "100"])
    assert result.output == ('\n' '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | XXX    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n' '\n' '\n')


@pytest.fixture
def add_system_to_temp_database(runner, config_tmp_path):
    """ Fixture to add and delete system from existing database """
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM"])
    yield result
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "delete",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER"])


def test_list_record_temp_db(runner, config_tmp_path, add_system_to_temp_database):
    """ Test LIST command with records in temporary database created with command line """
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, "list", "zzz", "100"])
    assert result.output == ('\n' '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | ZZZ    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n' '\n' '\n')


def test_update_record_temp_db(runner, config_tmp_path, db):
    """ Test UPDATE command in temporary database"""
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM"])
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "update",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "QAS_SYSTEM"])
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, "list", "zzz", "100"])
    assert result.output == ('\n' '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | ZZZ    | 100     | QAS_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n' '\n' '\n')


def test_delete_record_temp_db(runner, config_tmp_path, db):
    """ Test DELETE command in temporary database"""
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM"])
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "delete",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER"])
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, "list", "zzz", "100"])
    assert result.output == ('\n' '\n'
                             '+------------------------------------------------------------+\n'
                             '|         NOTHING FOUND according to search criteria         |\n'
                             '+------------+----------+-----------+----------------+-------+\n'
                             '| Customer   | System   | Mandant   | Description    | User  |\n'
                             '+------------+----------+-----------+----------------+-------+\n'
                             '|            | ZZZ      | 100       |                |       |\n'
                             '+------------+----------+-----------+----------------+-------+\n' '\n' '\n')


def test_pw_record_temp_db(runner, config_tmp_path, db):
    """ Test PW command in temporary database"""
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM"])
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "pw", "zzz", "100", "-c"])
    password = pyperclip.paste()

    assert password == '12345'


def test_debug_file(runner, config_tmp_path):
    """ Test DEBUG command to create debug file """
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, 'debug', '-f', '-o'])
    with open(os.path.join(config_tmp_path.config_path, DEBUG_FILE_NAME), mode='r') as f:
        text = f.read()
    assert text == '[FUNCTION]\nCommand =/H\nTitle=Debugger\nType=SystemCommand'


########################################################################################################################
# Test with already created config, encrypt keys and database
########################################################################################################################

@pytest.fixture
def add_system_to_existing_database(runner):
    """ Fixture to add and delete system from existing database """
    result = runner.invoke(sap_cli,
                           args=["add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM"])
    yield result
    result = runner.invoke(sap_cli,
                           args=["delete",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER"])


def test_list_record_exising_db(runner, add_system_to_existing_database):
    """ Test LIST command with records in database created with command line """
    result = runner.invoke(sap_cli, args=["list", "zzz", "100"])
    assert result.output == ('\n'
                             '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | ZZZ    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n' '\n' '\n')


def test_list_record_by_description_exising_db(runner, add_system_to_existing_database):
    """ Test LIST command with records in database created with command line """
    result = runner.invoke(sap_cli, args=["list", "-d", "sys"])
    assert result.output == ('\n'
                             '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | ZZZ    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n' '\n' '\n')


def test_list_record_by_customer_exising_db(runner, add_system_to_existing_database):
    """ Test LIST command with records in database created with command line """
    result = runner.invoke(sap_cli, args=["list", "-c", "cust"])
    assert result.output == ('\n'
                             '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | ZZZ    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n' '\n' '\n')


def test_pw_record_exising_db(runner, add_system_to_existing_database):
    """ Test PW command in existing database"""
    result = runner.invoke(sap_cli,
                           args=["pw", "zzz", "100", "-c"])
    password = pyperclip.paste()
    assert password == '12345'


def test_update_record_exising_db(runner, add_system_to_existing_database):
    """ Test UPDATE command in existing database"""
    result = runner.invoke(sap_cli,
                           args=["update",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "QAS_SYSTEM"])
    result = runner.invoke(sap_cli, args=["list", "zzz", "100"])
    assert result.output == ('\n' '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | ZZZ    | 100     | QAS_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n' '\n' '\n')
