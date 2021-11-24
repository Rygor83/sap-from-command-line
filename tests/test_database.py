#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import pytest
import os
from sap.database import SapDB
from sap.api import Sap_system
from sap.crypto import Crypto
from sap.file_names import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME


@pytest.fixture
def database(tmpdir):
    """ Initializing database with temporary path"""
    path = tmpdir.join('sap_db.db')
    return SapDB(db_path=path)


@pytest.fixture
def db(database, tmpdir):
    """ Creating temporary database """
    database.create()
    yield database
    database.stop_sap_db()
    database.drop()


@pytest.fixture
def crypto(tmpdir):
    crypto = Crypto(os.path.join(tmpdir, PUBLIC_KEY_NAME), os.path.join(tmpdir, PRIVATE_KEY_NAME))
    crypto.generate_keys()

    return crypto


@pytest.fixture
def added_record(db, crypto):
    """ Add temporary record for testing purpose """
    sys_list = ['XXX', '111', 'rygor', crypto.encrypto(str.encode('123')), 'TEST', 'Dev', '']
    system = Sap_system(*sys_list)
    db.add(system)
    return sys_list


def test_create_database(db):
    """ Test database creation """
    assert os.path.isfile(db.database_path) is True


def test_add_record_to_db(db, added_record):
    """ Test adding records to database """
    result_lst = db.query_system(Sap_system(system='XXX'))
    assert list(result_lst[0]) == added_record


def test_delete_record_from_db(db, added_record):
    """ Test deleting records from database """
    system = Sap_system(*added_record)
    db.delete(system)
    result_lst = db.query_system(Sap_system(system='XXX'))
    assert result_lst == []


def test_update_record(db, added_record, crypto):
    sys_list_updated = ['XXX', '111', 'rygor', crypto.encrypto(str.encode('123')), 'TEST_test', 'Development', '']
    system_updated = Sap_system(*sys_list_updated)
    db.update(system_updated)
    result_lst = db.query_system(Sap_system(system='XXX'))
    assert list(result_lst[0]) == sys_list_updated


def test_drop_database(database):
    database.create()
    database.drop()
    assert os.path.isfile(database.database_path) is False
