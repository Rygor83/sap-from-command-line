#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

from collections import namedtuple
from six import string_types

# Sap system parameters : [system: str, mandant: int, user: str, password: byte]
Sap_system = namedtuple('SAP', ['system', 'mandant', 'user', 'password', 'transaction'])
Sap_system.__new__.__defaults__ = (None, None, None, None, None)


# custom exceptions
class TasksException(Exception):
    """A tasks error has occurred."""


class UninitializedDatabase(TasksException):
    """Call tasks.start_tasks_db() before other functions."""


def pw(sap_system):
    return _sapdb.pw(sap_system)


def run(sap_system):
    """ Запуск указанной SAP системы \n Обязательные параметры: 1. система, 2. мандант (не обязательно)  """
    return _sapdb.run(sap_system)


def database():
    pass


def add(sap_system: Sap_system):
    if not isinstance(sap_system, Sap_system):
        raise TypeError('sap must be Sap object')
    if not isinstance(sap_system.system, str):
        raise ValueError('sap.system must be string')
    if not sap_system.mandant.isnumeric():
        raise ValueError('sap.mandant must contain only numbers')
    if not isinstance(sap_system.user, str):
        raise ValueError('sap.user must be str')
    if not isinstance(sap_system.password, bytes):
        raise ValueError('sap.password must be str')
    if _sapdb is None:
        raise UninitializedDatabase()

    return _sapdb.add(sap_system)


def update(sap_system: Sap_system):
    if not isinstance(sap_system, Sap_system):
        raise TypeError('sap must be Sap object')
    if not isinstance(sap_system.system, str):
        raise ValueError('sap.system must be string')
    if not sap_system.mandant.isnumeric():
        raise ValueError('sap.mandant must contain only numbers')
    if not isinstance(sap_system.user, str):
        raise ValueError('sap.user must be str')

    return _sapdb.update(sap_system)


def delete(sap_system: Sap_system):
    if not isinstance(sap_system, Sap_system):
        raise TypeError('sap must be Sap object')
    if not isinstance(sap_system.system, str):
        raise ValueError('sap.system must be string')
    if not sap_system.mandant.isnumeric():
        raise ValueError('sap.mandant must contain only numbers')
    if not isinstance(sap_system.user, str):
        raise ValueError('sap.user must be str')

    return _sapdb.delete(sap_system)


def list_systems(system):
    # if not isinstance(system, str):
    #     raise ValueError('sap.system must be string')
    return _sapdb.list_systems(system)


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
