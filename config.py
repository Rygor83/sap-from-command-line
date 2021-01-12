#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import configparser
import ctypes
import functools
import os
import sys
import click

from termcolor import colored

import crypto as cr


class Config(object):
    ini_file = 'config.ini'

    def __init__(self):
        self.data = {'CONNECTION': {}, 'APPLICATION': {}, 'KEYS': {}, 'LANGUAGE': {}}

    @functools.lru_cache()
    def read(self):

        if not os.path.isfile(self.ini_file) or not os.stat(self.ini_file).st_size != 0:
            # TODO: переделать сообщиние, чтоб мол нет доступа к ини файлу т.к. его или не существует, или нет доступа.
            # TODO: Сделать не только уведомление, но так же попытка запустить контейнер, где располагается БД
            click.echo(click.style('Не удалось получить нужные параметры т.к. ini файла не существует. \n', bg='black',
                                   fg='yellow'))
            click.echo('Для создания запустите команду "ini" и укажите в созданном файле все требуетмые параметры \n')
            click.pause('Нажмите для продолжения ...')
            sys.exit()

        config = configparser.ConfigParser()

        read = config.read(self.ini_file)
        if not read:
            click.echo(colored(f'Не удалось прочитать ini файл {self.ini_file}', 'yellow'))
            click.pause('Нажмите для продолжения ...')
        else:
            self.data['DATABASE'] = config['DATABASE']
            self.data['APPLICATION'] = config['APPLICATION']
            self.data['KEYS'] = config['KEYS']
            self.data['LANGUAGE'] = config['LANGUAGE']

    def create(self):
        config = configparser.ConfigParser()
        config['DATABASE'] = {'path': 'путь к базе данных'}

        config['APPLICATION'] = {'command_line': 'путь до файла sapshcut.exe',
                                 'sap': 'путь до файла saplogon.exe'}

        config['KEYS'] = {cr.Crypto.public_file: 'путь до публичного ключа',
                          cr.Crypto.private_file: 'путь до приватного ключа. !!! ключ хранить в защищенном хранилище'}

        # Определение языка
        win_dll = ctypes.windll.kernel32
        lng_code = win_dll.GetUserDefaultUILanguage()
        if lng_code == 1049:
            ini_lang = 'RU'
        else:
            ini_lang = 'EN'
        config['LANGUAGE'] = {'language': ini_lang}

        with open(self.ini_file, 'w') as configfile:
            config.write(configfile)

        click.echo('Путь: %s \n' % click.format_filename(self.ini_file))
        click.echo(click.style('INI файл создан', bg='black', fg='green'))
        click.echo(click.style('!!! Заполните все требуемые параметры в файле !!! \n', bg='black', fg='white'))
        click.pause('Нажмите для продолжения ...')

        click.launch(self.ini_file)

    def exists(self):
        if os.path.isfile(self.ini_file):
            return True
        else:
            return False
