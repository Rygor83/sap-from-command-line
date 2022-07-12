#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Database Tests """

import pytest
import os
from sap.database import SapDB
from sap.api import Sap_system
from sap.crypto import Crypto
from api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, DATABASE_NAME


@pytest.fixture
def database(tmpdir):
    """ Initializing database with temporary path"""
    path = tmpdir.join(DATABASE_NAME)
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
    yield crypto
    crypto.remove_keys()


@pytest.fixture
def added_record(db, crypto):
    """ Add temporary record for testing purpose """
    system = Sap_system(system='XXX', mandant='111', user='rygor', password=crypto.encrypto(str.encode('123')),
                        customer='Test', description='Dev', url='')
    db.add(system)
    return system


def test_create_database(db):
    """ Test database creation """
    assert os.path.isfile(db.database_path) is True


def test_add_record_to_db(db, added_record):
    """ Test adding records to database """
    result_lst = db.query_system(Sap_system(system='XXX'))
    assert Sap_system(*result_lst[0]) == added_record


def test_delete_record_from_db(db, added_record):
    """ Test deleting records from database """
    system = Sap_system(*added_record)
    db.delete(system)
    result_lst = db.query_system(Sap_system(system='XXX'))
    assert result_lst == []


def test_update_record(db, added_record, crypto):
    system_updated = Sap_system(system='XXX', mandant='111', user='rygor', password=crypto.encrypto(str.encode('123')),
                                customer='TEST_test', description='Development',
                                url='')
    db.update(system_updated)
    result_lst = db.query_system(Sap_system(system='XXX', mandant='111', user='rygor'))
    assert Sap_system(*result_lst[0]) == system_updated


def test_drop_database(database):
    database.create()
    database.drop()
    assert os.path.isfile(database.database_path) is False
