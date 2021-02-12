#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

from collections import namedtuple
from configparser import ConfigParser
import ctypes
import os
import click

SapConfig = namedtuple('SapConfig', ['db_path', 'db_type', 'command_line_path', 'saplogon_path', 'public_key_path',
                                     'private_key_path', 'language'])


class Config(object):

    def __init__(self):
        self.ini_file_path = 'config.ini'

    def read(self):
        """Return SapConfig object after reading config file."""
        parser = ConfigParser()
        if not self.exists():
            self.create()
        else:
            a = parser.read(self.ini_file_path)

            db_path = parser.get('DATABASE', 'db_path')
            db_type = parser.get('DATABASE', 'db_type')
            command_line_path = parser.get('APPLICATION', 'command_line_path')
            saplogon_path = parser.get('APPLICATION', 'saplogon_path')
            public_key_path = parser.get('KEYS', 'public_key_path')
            private_key_path = parser.get('KEYS', 'private_key_path')
            language = parser.get('LOCALE', 'language')

            return SapConfig(db_path, db_type, command_line_path, saplogon_path, public_key_path, private_key_path,
                             language)

    def create(self):
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

        with open(self.ini_file_path, 'w') as configfile:
            parser.write(configfile)

        click.echo('Путь: %s \n' % click.format_filename(self.ini_file_path))
        click.echo(click.style('INI файл создан', bg='black', fg='green'))
        click.echo(click.style('!!! Заполните все требуемые параметры в файле !!! \n', bg='black', fg='white'))
        click.pause('Нажмите для продолжения ...')

        click.launch(self.ini_file_path)

    def exists(self):
        if os.path.exists(self.ini_file_path):
            return True
        else:
            return False
