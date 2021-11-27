#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Config file management """

import ctypes
import os
from collections import namedtuple
from configparser import ConfigParser
import click
from sap import utilities
import pathlib
import typing

from sap.exceptions import FileDoesNotExists, ConfigExists, ConfigDoesNotExists
from sap.file_names import PRIVATE_KEY_NAME, PUBLIC_KEY_NAME, CONFIG_NAME, DATABASE_NAME

SapConfig = namedtuple('SapConfig', ['db_path', 'db_type', 'command_line_path', 'saplogon_path', 'public_key_path',
                                     'private_key_path', 'language'])


class Config:
    """
    Class for working with config file: create, read
    """

    def __init__(
            self,
            config_path: typing.Union[str, pathlib.Path] = None,
            db_path=None,
            db_type='sqlite',
            command_line_path=None,
            saplogon_path=None,
            public_key_path=None,
            private_key_path=None

    ):

        self.ini_name = CONFIG_NAME
        self.config_path = config_path if config_path else utilities.path()
        self.config_file_path = os.path.join(config_path, self.ini_name) if config_path else os.path.join(
            utilities.path(), self.ini_name)

        self.db_path = db_path if db_path else os.path.join(self.config_path, DATABASE_NAME)
        self.db_type = db_type
        self.command_line_path = command_line_path if command_line_path else 'path to sapshcut.exe file'
        self.saplogon_path = saplogon_path if saplogon_path else 'path to saplogon.exe file'
        self.public_key_path = public_key_path if public_key_path else os.path.join(self.config_path,
                                                                                    PUBLIC_KEY_NAME)
        self.private_key_path = private_key_path if private_key_path else os.path.join(self.config_path,
                                                                                       PRIVATE_KEY_NAME)
        self.language = 'RU'

        # if not self.exists():
        #     self.db_path = db_path if db_path else os.path.join(self.config_path, DATABASE_NAME)
        #     self.db_type = db_type
        #     self.command_line_path = command_line_path if command_line_path else 'path to sapshcut.exe file'
        #     self.saplogon_path = saplogon_path if saplogon_path else 'path to saplogon.exe file'
        #     self.public_key_path = public_key_path if public_key_path else os.path.join(self.config_path,
        #                                                                                 PUBLIC_KEY_NAME)
        #     self.private_key_path = private_key_path if private_key_path else os.path.join(self.config_path,
        #                                                                                    PRIVATE_KEY_NAME)

    def read(self):
        """Return SapConfig object after reading config file."""
        parser = ConfigParser()

        if self.exists():
            parser.read(self.config_file_path)

            self.db_path = parser.get('DATABASE', 'db_path')
            self.db_type = parser.get('DATABASE', 'db_type')
            self.command_line_path = parser.get('APPLICATION', 'command_line_path')
            self.saplogon_path = parser.get('APPLICATION', 'saplogon_path')
            self.public_key_path = parser.get('KEYS', 'public_key_path')
            self.private_key_path = parser.get('KEYS', 'private_key_path')
            self.language = parser.get('LOCALE', 'language')

            # if not os.path.exists(command_line_path):
            #     raise FileDoesNotExists(command_line_path, "[APPLICATION], 'command_line_path'")
            # if not os.path.exists(saplogon_path):
            #     raise FileDoesNotExists(command_line_path, "[APPLICATION], 'saplogon_path'")
            # if not os.path.exists(public_key_path):
            #     raise FileDoesNotExists(command_line_path, "[KEYS], 'public_key_path'")
            # if not os.path.exists(private_key_path):
            #     raise FileDoesNotExists(command_line_path, "[KEYS], 'private_key_path'")

            return SapConfig(self.db_path, self.db_type, self.command_line_path, self.saplogon_path,
                             self.public_key_path, self.private_key_path, self.language)
        else:
            raise ConfigDoesNotExists(self.config_path)

    def create(self):
        """
        Create configuration file
        """
        if os.path.exists(self.config_file_path):
            raise ConfigExists(self.config_file_path)
        else:
            parser = ConfigParser(allow_no_value=True)
            parser['DATABASE'] = {
                "; DB_PATH - Path to database. Database file must be placed in secure place": None,
                'db_path': self.db_path,
                "; DB_TYPE - database type. Default: sqlite": None,
                'db_type': self.db_type}

            parser['APPLICATION'] = {
                "; COMMAND_LINE_PATH - Path to sapshcut.exe file": None,
                'command_line_path': self.command_line_path,
                "; SAPLOGON_PATH - Path to saplogon.exe file": None,
                'saplogon_path': self.saplogon_path}

            parser['KEYS'] = {
                "; public_key_path - Path to public_key_file_name encryption key": None,
                'public_key_path': self.public_key_path,
                "; PRIVATE_KEY_PATH - Path to private_key_file_name encryption key. Private key must be placed in secure place": None,
                'private_key_path': self.private_key_path}

        # Определение языка
        win_dll = ctypes.windll.kernel32
        lng_code = win_dll.GetUserDefaultUILanguage()
        if lng_code == 1049:
            ini_lang = 'RU'
        else:
            ini_lang = 'EN'
        parser['LOCALE'] = {'language': ini_lang}

        with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
            parser.write(configfile)

    def exists(self):
        """
        Check if config path is valid
        """
        return os.path.exists(self.config_file_path)

    def open_config(self):
        """
        Open config file in editor
        """
        click.launch(url=self.config_file_path)

    def remove_config(self):
        """ Remove encryption keys """
        os.remove(self.config_file_path)


def open_config(ctx, param, value):
    """
    Open configuration file for editing
    """
    if not value or ctx.resilient_parsing:
        return
    # cfg = Config()
    ctx.obj.config.open_config()
    ctx.exit()


def create_config(ctx, param, value):
    """
    Open configuration file for editing
    """
    if not value or ctx.resilient_parsing:
        return

    # cfg = Config()
    if ctx.obj.config.exists():
        click.echo(click.style("Config уже существует \n", **utilities.color_warning))
        click.echo(utilities.path())
    else:
        ctx.obj.config.create()
    ctx.exit()
