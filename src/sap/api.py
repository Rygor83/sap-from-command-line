#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" sap's module API """

from collections import namedtuple
import click
from sap.exceptions import DatabaseDoesNotExists

Sap_system = namedtuple('SAP', ['system', 'mandant', 'user', 'password', 'language', 'customer', 'description', 'url',
                                'autotype', 'only_web'])
Sap_system.__new__.__defaults__ = (None, None, None, None, None, None, None, None, None)

Parameter = namedtuple('parameters', ['transaction', 'parameter'])
Parameter.__new__.__defaults__ = (None, None)


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

    # noinspection PyUnresolvedReferences
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

    # noinspection PyUnresolvedReferences
    return _sapdb.add(sap_system)


# noinspection PyUnresolvedReferences
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


# noinspection PyUnresolvedReferences
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


# noinspection PyUnresolvedReferences
def query_param(parameter: Parameter):
    return _sapdb.query_param(parameter)


# noinspection PyUnresolvedReferences
def add_param(parameter: Parameter):
    return _sapdb.add_param(parameter)


# noinspection PyUnresolvedReferences
def delete_param(parameter: Parameter):
    return _sapdb.delete_param(parameter)


# noinspection PyUnresolvedReferences
def update_param(parameter: Parameter):
    return _sapdb.update_param(parameter)


_sapdb = None


def start_sap_db(db_path, db_type):
    """Connect API functions to a db."""
    # if not isinstance(db_path, string_types):
    #     raise TypeError('db_path must be a string')
    global _sapdb
    import sap.database
    try:
        _sapdb = sap.database.start_sap_db(db_path, db_type)
        _sapdb.make_session()
    except DatabaseDoesNotExists as err:
        click.echo(f"{err.message}")
        raise click.Abort


# noinspection PyUnresolvedReferences
def stop_sap_db():
    _sapdb.stop_sap_db()


class Obj_structure:
    def __init__(self):
        self.config = None
        self.crypto = None
        self.database = None


# File names
PUBLIC_KEY_NAME = 'public_key.txt'
PRIVATE_KEY_NAME = 'private_key.txt'
CONFIG_NAME = 'sap_config.ini'
DATABASE_NAME = 'database.db'
COMMAND_LINE_NAME = 'sapshcut.exe'
SAPLOGON_NAME = 'saplogon.exe'
DEBUG_FILE_NAME = "DEBUG.TXT"
SAPLOGON_INI = 'SAPUILandscape.xml'
TEXT_FILE_NAME = 'text_file.txt'
