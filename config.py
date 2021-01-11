#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
import configparser
import functools
import os
import sys

from termcolor import colored


class Config(object):
    ini_file = 'config.ini'

    def __init__(self):
        self.config = {'CONNECTION': {}, 'APPLICATION': {}, 'KEYS': {}, 'LANGUAGE': {}}

    @functools.lru_cache()
    def get_config(self):

        if not os.path.isfile(self.ini_file) or not os.stat(self.ini_file).st_size != 0:
            # TODO: переделать сообщиние, чтоб мол нет доступа к ини файлу т.к. его или не существует, или нет доступа.
            # TODO: Сделать не только уведомление, но так же попытка запустить контейнер, где располагается БД
            print(colored('Не удалось получить нужные параметры т.к. ini файла не существует.'), 'yellow')
            print('Для создания запустите команду "ini" и укажите в созданном файле все требуетмые параметры')
            input('Нажмите для продолжения')
            sys.exit()

        config = configparser.ConfigParser()

        read = config.read(self.ini_file)
        if not read:
            print(colored(f'Не удалось прочитать ini файл {self.ini_file}', 'yellow'))
            input('Нажмите для продолжения')
        else:
            self.config['DATABASE'] = config['DATABASE']
            self.config['APPLICATION'] = config['APPLICATION']
            self.config['KEYS'] = config['KEYS']
            self.config['LANGUAGE'] = config['LANGUAGE']
