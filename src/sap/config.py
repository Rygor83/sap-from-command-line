#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import ctypes
import os
import click
import sap.utilities as utilities
from collections import namedtuple
from configparser import ConfigParser

SapConfig = namedtuple('SapConfig', ['db_path', 'db_type', 'command_line_path', 'saplogon_path', 'public_key_path',
                                     'private_key_path', 'language'])


class Config(object):
    """
    Class for working with config file: create, read
    """

    def __init__(self):
        self.ini_name = 'sap_config.ini'
        self.config_path = os.path.join(utilities.path(), self.ini_name)

    def read(self):
        """Return SapConfig object after reading config file."""
        parser = ConfigParser()
        if not self.exists():
            self.create()
        else:
            a = parser.read(self.config_path)

            db_path = parser.get('DATABASE', 'db_path')
            db_type = parser.get('DATABASE', 'db_type')
            command_line_path = parser.get('APPLICATION', 'command_line_path')
            saplogon_path = parser.get('APPLICATION', 'saplogon_path')
            public_key_path = parser.get('KEYS', 'public_key_path')
            private_key_path = parser.get('KEYS', 'private_key_path')
            language = parser.get('LOCALE', 'language')

            if not os.path.exists(command_line_path):
                raise FileDoesNotExists(command_line_path, "[APPLICATION], 'command_line_path'")
            if not os.path.exists(saplogon_path):
                raise FileDoesNotExists(command_line_path, "[APPLICATION], 'saplogon_path'")
            if not os.path.exists(public_key_path):
                raise FileDoesNotExists(command_line_path, "[KEYS], 'public_key_path'")
            if not os.path.exists(private_key_path):
                raise FileDoesNotExists(command_line_path, "[KEYS], 'private_key_path'")

            return SapConfig(db_path, db_type, command_line_path, saplogon_path, public_key_path, private_key_path,
                             language)

    def create(self):
        """
        Create configuration file
        """
        if os.path.exists(self.config_path):
            raise ConfigExists(self.config_path)
        else:
            parser = ConfigParser()
            parser['DATABASE'] = {'db_path': 'database.db',
                                  'db_type': 'sqlite'}

            parser['APPLICATION'] = {'command_line_path': 'путь до файла sapshcut.exe',
                                     'saplogon_path': 'путь до файла saplogon.exe'}

            parser['KEYS'] = {'public_key_path': 'путь до публичного ключа',
                              'private_key_path': 'путь до приватного ключа. !!! ключ хранить в защищенном хранилище'}

            # Определение языка
            win_dll = ctypes.windll.kernel32
            lng_code = win_dll.GetUserDefaultUILanguage()
            if lng_code == 1049:
                ini_lang = 'RU'
            else:
                ini_lang = 'EN'
            parser['LOCALE'] = {'language': ini_lang}

            with open(self.config_path, 'w') as configfile:
                parser.write(configfile)

    def exists(self):
        """
        Check if config path is valid
        """
        if os.path.exists(self.config_path):
            return True
        else:
            return False

    def open_config(self):
        """
        Open config file in editor
        """
        click.launch(self.config_path)


class ConfigExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, config_path, message="sap_config.ini already exists"):
        self.message = f"{message}. Path: {config_path}"
        super().__init__(self.message)


class FileDoesNotExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, path, file_name):
        self.message = f"Parameters {file_name}. Path does not exist: {path}"
        super().__init__(self.message)
