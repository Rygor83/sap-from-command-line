#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import pytest
import os
from click.testing import CliRunner
from sap.database import SapDB
from sap.api import Sap_system


@pytest.fixture
def database(tmpdir):
    return SapDB(db_path=tmpdir, db_type='')


@pytest.fixture
def db(database, tmpdir):
    db = database
    db.create()
    yield
    db.delete(Sap_system('XXX', '100', 'Rygor', '12345678', '', 'AK', 'Test system'))


def test_add(db):
    system = Sap_system('XXX', '100', 'Rygor', '12345678', '', 'AK', 'Test system')
    db.add(system)
    assert db.list_systems('XXX')
