#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import pytest
import click
import os
from click.testing import CliRunner
from sap.database import SapDB
from sap.api import Sap_system
from sap.crypto import Crypto


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


def test_add(db):
    sys_list = ['XXX', '111', 'rygor', Crypto.encrypto(str.encode('123')), '', 'AK', 'Dev']
    system = Sap_system(*sys_list)
    db.add(system)
    del sys_list[4]
    result_lst = db.query_system(Sap_system(system='XXX'))
    assert list(result_lst[0]) == sys_list


def test_delete(db):
    sys_list = ['XXX', '111', 'rygor', Crypto.encrypto(str.encode('123')), '', 'AK', 'Dev']
    system = Sap_system(*sys_list)
    db.add(system)
    db.delete(system)
    del sys_list[4]
    result_lst = db.query_system(Sap_system(system='XXX'))
    assert result_lst == []
