#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Config file management """

import ctypes
import os
from collections import namedtuple
from configparser import ConfigParser
import pathlib
import typing
import click
from sap import utilities

from sap.exceptions import ConfigExists, ConfigDoesNotExists
from sap.api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME

SapConfig = namedtuple('SapConfig', ['db_path', 'db_type', 'command_line_path', 'saplogon_path', 'public_key_path',
                                     'private_key_path', 'language', 'sequence', 'wait_site_to_load', 'time_to_clear'])


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
            private_key_path=None,
            sequence=None,
            wait_site_to_load=None,
            time_to_clear=None,
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
        self.language = 'RU'  # TODO: сделать мультиязычность

        self.sequence = sequence
        self.wait_site_to_load = wait_site_to_load

        self.time_to_clear = time_to_clear

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

            self.sequence = parser.get('AUTO-TYPE', 'sequence')
            self.wait_site_to_load = int(parser.get('AUTO-TYPE', 'wait'))

            self.time_to_clear = int(parser.get('PASSWORD', 'time_to_clear'))

            # TODO: Сделать проверку и уведомление, если приватный ключ и базаданных лежат в одной папке

            # db_path = pathlib.Path(self.db_path)
            # private_key_path = pathlib.Path(self.private_key_path)
            # if db_path.parent == private_key_path.parent:
            #     click.echo(click.style(
            #         f"\nPrivate key ({db_path}) file and Database ({private_key_path}) file have to be in a separate folders for safety reason.",
            #         bg='red', fg='white'))

            return SapConfig(self.db_path, self.db_type, self.command_line_path, self.saplogon_path,
                             self.public_key_path, self.private_key_path, self.language, self.sequence,
                             self.wait_site_to_load, self.time_to_clear)
        else:
            raise ConfigDoesNotExists(self.config_file_path)

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

            parser['AUTO-TYPE'] = {
                "; sequence - default autotype sequence": None,
                'sequence': "{USER}{TAB}{PASS}{ENTER}",
                "; wait - Time to wait a web site to load": None,
                'wait': 4}

            parser['PASSWORD'] = {
                "; time_to_clear - Time to wait to clear clipboard with password": None,
                'time_to_clear': 10}

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

    def open_config(self, locate=False):
        """
        Open config file in editor
        ::param locate: True - open folder or web, False - open application
        """
        return click.launch(url=self.config_file_path, locate=locate)

    def remove_config(self):
        """ Remove encryption keys """
        os.remove(self.config_file_path)


def create_config(ctx, param, value):
    """
    Open configuration file for editing
    """
    if not value or ctx.resilient_parsing:
        return

    try:
        ctx.obj.config.create()
    except ConfigExists as err:
        utilities.print_message(f"{err}", message_type=utilities.message_type_error)
        raise click.Abort

    click.launch(ctx.obj.config.config_file_path, locate=True)

    ctx.exit()


def open_config(ctx, param, value):
    """
    Open configuration file for editing
    """
    if not value or ctx.resilient_parsing:
        return
    utilities.print_message(f"Opening file: {ctx.obj.config.config_file_path}",
                            message_type=utilities.message_type_message)
    ctx.obj.config.open_config()
    ctx.exit()


def open_folder(ctx, param, value):
    """
     Open configuration file folder
    """
    if not value or ctx.resilient_parsing:
        return

    utilities.print_message(f"Opening folder: {utilities.path()}",
                            message_type=utilities.message_type_message)
    ctx.obj.config.open_config(locate=True)

    ctx.exit()
