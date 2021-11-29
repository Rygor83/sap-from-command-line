#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Test for Command Line """

import os

import click
import pytest
import pyperclip
import time

from click.testing import CliRunner
from sap.cli import sap_cli, delete
from sap.database import SapDB
from sap.crypto import Crypto
from sap.api import Sap_system
from sap.config import Config
from api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, COMMAND_LINE_PATH, SAPLOGON_PATH, \
    DEBUG_FILE_NAME


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
def temp_db(tmp_path):
    """ Prepare temporary database """
    database_path = tmp_path.joinpath(DATABASE_NAME)
    database = SapDB(db_path=database_path)
    database.create()
    yield database
    database.stop_sap_db()
    database.drop()


@pytest.fixture
def added_record(temp_db, crypto):
    """ Add temporary record for testing purpose """
    system = Sap_system('XXX', '100', 'USER', crypto.encrypto(str.encode('123')), 'CUSTOMER', 'DEV_SYSTEM', '')
    temp_db.add(system)


@pytest.fixture
def config_tmp_path(tmp_path, crypto):
    """ Create specific config with tmp_dir """
    cfg = Config(config_path=tmp_path,
                 db_path=tmp_path.joinpath(DATABASE_NAME),
                 # db_path=temp_db.database_path,
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


def test_list_added_system_outside_comman_line(runner, config_tmp_path, added_record, temp_db):
    """ Test LIST command with records in temporary database created from api"""
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, "list", "xxx", "100"])
    assert result.output == ('\n' '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | XXX    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n')


@pytest.fixture
def add_system_to_temp_database(temp_db, config_tmp_path, runner):
    """ Fixture to add and delete system from existing database """
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM",
                                 "-url", "", '-v'])
    # yield result
    # result = runner.invoke(sap_cli,
    #                        args=["-path", config_tmp_path.config_path,
    #                              "delete", "zzz", "100", "-confirm", "y"])


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
                             '+----------+--------+---------+-------------+------+\n')


def test_delete_record_temp_db(temp_db, config_tmp_path, runner):
    """ Test DELETE command in temporary database"""
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM",
                                 "-url", " ", '-v'])
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path, "delete", "zzz", "100", "-confirm", "y"])
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, "list", "zzz", "100"])
    assert result.output == ('\n' '\n'
                             '+------------------------------------------------------------+\n'
                             '|         NOTHING FOUND according to search criteria         |\n'
                             '+------------+----------+-----------+----------------+-------+\n'
                             '| Customer   | System   | Mandant   | Description    | User  |\n'
                             '+------------+----------+-----------+----------------+-------+\n'
                             '|            | ZZZ      | 100       |                |       |\n'
                             '+------------+----------+-----------+----------------+-------+\n')


def test_pw_record_temp_db(runner, temp_db, config_tmp_path):
    """ Test PW command in temporary database"""
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM",
                                 "-url", "", '-v'])
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


def test_update_record_temp_db(runner, temp_db, config_tmp_path):
    """ Test UPDATE command in temporary database"""
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "add",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "DEV_SYSTEM",
                                 "-url", "", '-v'])
    result = runner.invoke(sap_cli,
                           args=["-path", config_tmp_path.config_path,
                                 "update",
                                 "-system", "zzz",
                                 "-mandant", "100",
                                 "-user", "USER",
                                 "-password", "12345",
                                 "-customer", "CUSTOMER",
                                 "-description", "QAS_SYSTEM",
                                 "-url", " "])
    result = runner.invoke(sap_cli, args=["-path", config_tmp_path.config_path, "list", "zzz", "100"])
    assert result.output == ('\n' '\n'
                             '+--------------------------------------------------+\n'
                             '|                Available systems                 |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| Customer | System | Mandant | Description | User |\n'
                             '+----------+--------+---------+-------------+------+\n'
                             '| CUSTOMER | ZZZ    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n')


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
                                 "-description", "DEV_SYSTEM",
                                 "-url", "", '-v'])
    yield result
    result = runner.invoke(sap_cli,
                           args=["delete", "zzz", "100", "-confirm", "y"])


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
                             '+----------+--------+---------+-------------+------+\n')


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
                             '+----------+--------+---------+-------------+------+\n')


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
                             '+----------+--------+---------+-------------+------+\n')


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
                             '| CUSTOMER | ZZZ    | 100     | DEV_SYSTEM  | USER |\n'
                             '+----------+--------+---------+-------------+------+\n')