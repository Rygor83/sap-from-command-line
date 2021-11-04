#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

from collections import namedtuple
from six import string_types
import sqlalchemy
import click

# Sap system parameters : [system: str, mandant: int, user: str, password: byte]
Sap_system = namedtuple('SAP', ['system', 'mandant', 'user', 'password', 'transaction', 'customer', 'description'])
Sap_system.__new__.__defaults__ = (None, None, None, None, None, None, None)


def query_system(sap_system: Sap_system):
    """ Запуск указанной SAP системы \n Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    # if not isinstance(sap_system, Sap_system):
    #     raise TypeError('sap must be Sap object')
    # if not isinstance(sap_system.system, str) and sap_system.system is not None:
    #     raise ValueError('sap.system must be string')
    # if not sap_system.mandant.isnumeric() and sap_system.mandant is not None:
    #     raise ValueError('sap.mandant must contain only numbers')
    # if not isinstance(sap_system.user, str) and sap_system.user is not None:
    #     raise ValueError('sap.user must be str')
    # if not isinstance(sap_system.password, bytes) and sap_system.password is not None:
    #     raise ValueError('sap.password must be str')
    # if not isinstance(sap_system.description, str) and sap_system.description is not None:
    #     raise ValueError('sap.description must be string')
    # if _sapdb is None:
    #     raise UninitializedDatabase()

    return _sapdb.query_system(sap_system)


def add(sap_system: Sap_system):
    # if not isinstance(sap_system, Sap_system):
    #     raise TypeError('sap must be Sap object')
    # if not isinstance(sap_system.system, str):
    #     raise ValueError('sap.system must be string')
    # if not sap_system.mandant.isnumeric():
    #     raise ValueError('sap.mandant must contain only numbers')
    # if not isinstance(sap_system.user, str):
    #     raise ValueError('sap.user must be str')
    # if not isinstance(sap_system.password, bytes):
    #     raise ValueError('sap.password must be str')
    # if not isinstance(sap_system.description, str):
    #     raise ValueError('sap.description must be string')
    # if _sapdb is None:
    #     raise UninitializedDatabase()

    return _sapdb.add(sap_system)


def update(sap_system: Sap_system):
    # if not isinstance(sap_system, Sap_system):
    #     raise TypeError('sap must be Sap object')
    # if not isinstance(sap_system.system, str):
    #     raise ValueError('sap.system must be string')
    # if not sap_system.mandant.isnumeric():
    #     raise ValueError('sap.mandant must contain only numbers')
    # if not isinstance(sap_system.user, str):
    #     raise ValueError('sap.user must be str')

    return _sapdb.update(sap_system)


def delete(sap_system: Sap_system):
    # if not isinstance(sap_system, Sap_system):
    #     raise TypeError('sap must be Sap object')
    # if not isinstance(sap_system.system, str):
    #     raise ValueError('sap.system must be string')
    # if not sap_system.mandant.isnumeric():
    #     raise ValueError('sap.mandant must contain only numbers')
    # if not isinstance(sap_system.user, str):
    #     raise ValueError('sap.user must be str')

    return _sapdb.delete(sap_system)


def query_param(transaction):
    return _sapdb.query_param(transaction)


_sapdb = None
_config = None


def start_sap_db(db_path, db_type):
    """Connect API functions to a db."""
    if not isinstance(db_path, string_types):
        raise TypeError('db_path must be a string')
    global _sapdb
    import sap.database
    _sapdb = sap.database.start_sap_db(db_path, db_type)


def stop_sap_db():
    _sapdb.stop_sap_db()
