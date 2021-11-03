#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import click
import sys
import traceback
import os
import subprocess

from appdirs import *
from sap.api import Sap_system
from prettytable import PrettyTable
from operator import attrgetter

# Цвета сообщений
color_message = {'bg': 'black', 'fg': 'white'}
color_success = {'bg': 'black', 'fg': 'green'}
color_warning = {'bg': 'black', 'fg': 'yellow'}
color_sensitive = {'bg': 'red', 'fg': 'white'}

# Заголовки таблиц
header_nsmup = ['№', 'Система', 'Мандант', 'Пользователь', 'Пароль']  # NSMUP: Number, System, Mandant, User, Password
header_nsmu = ['№', 'Система', 'Мандант', 'Пользователь']  # NSMU: Number, System, Mandant, User
header_nsmut = ['№', 'Система', 'Мандант', 'Пользователь', 'Транзакция']  # NSMU: Number, System, Mandant, User
header_nsmutp = ['№', 'Система', 'Мандант', 'Пользователь', 'Пароль',
                 'Транзакция']  # NSMU: Number, System, Mandant, User, Password, Transaction
header_nsm = ['№', 'Система', 'Мандант']  # NSM: Number, System, Mandant


def launch_command_line_with_params(command_line_path, param):
    ''' Запуск sapshcut.exe с разными параметрами'''
    if not os.path.exists(command_line_path):
        click.echo(
            click.style(f'Путь до sapshcut.exe не верный: \n{command_line_path} \n', **color_warning))
        sys.exit()

    # Добавляем путь к командному файлу
    argument = [command_line_path, param]

    # Запускаем SAP
    subprocess.call(argument)


def choose_system(result, verbose=False):
    ans = 0
    if len(result) >= 2:
        print_system_list(result, 'Доступные системы', header_nsmu, verbose=verbose)

        while int(ans) > len(result) or int(ans) < 1:
            if 1 <= int(ans) <= len(result):
                break
            click.echo(click.style(f"\nВозможно вводить значения только от 1 до {str(len(result))}.",
                                   **color_message))
            ans = click.prompt('Выберите систему, в которую хотите войти \n>>>', type=int)
        ans = ans - 1

    system = Sap_system(result[ans].system, result[ans].mandant, result[ans].user, result[ans].password,
                        result[ans].transaction, result[ans].customer, result[ans].description)
    return system


def print_system_list(systems: list, title, header: list, verbose=False):
    # TODO: Сделать универсальным:
    #  на вход подавать так же и заголовок.
    #  Затем функцию подавать в:
    #  1. Когда пытаемся запустить системы: мол пробуем запустить то-то и то-то
    #     вместо модуля NO_RESULT_OUTPUT
    #  2. Когда не удалось получить данные системы

    sorted_systems = sorted(systems, key=attrgetter('system', 'mandant'))

    if verbose:
        header.append('Пароль')
        header.append('Заказчик')
        header.append('Описание')
    else:
        header.append('Заказчик')
        header.append('Описание')

    # Создаем таблицу
    t = PrettyTable(header)

    # Добавление информации в табилцу
    for num, system in enumerate(sorted_systems, start=1):
        row = [num, system.system]
        if system.mandant:
            row.append(system.mandant)
        if system.user:
            row.append(system.user)
            t.align["Пользователь"] = "l"
        if system.transaction:
            row.append(system.transaction)
        if verbose:
            row.append(system.password)
            t.align["Пароль"] = "l"
        if system.customer:
            row.append(system.customer)
            t.align["Заказчик"] = "l"
        if system.description:
            row.append(system.description)
            t.align["Описание"] = "l"
        t.add_row(row)

    # Вывод информации
    click.echo('\n')
    click.echo(t.get_string(title=click.style(title, **color_success)))


def no_result_output(system, mandant='', user=''):
    ''' Выводит сообщение, если не получилось достать из базы данных информацию
        Так же выводит данные запроса'''
    click.echo(click.style(f'\nПо запрошенным данным системы в базе данных отсутствую:', **color_success))
    if system:
        click.echo(f'Система: {str(system).upper()}')
    if mandant:
        click.echo(f'Мандант: {mandant}')
    if user:
        click.echo(f'Пользователь: {str(user).upper()}')
    sys.exit()


def show_exception_and_exit(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb)
    sys.exit(-1)


def path():
    return user_data_dir('sap', appauthor=False)


def get_run_parameters(system, mandant='', user='', password='', language='RU', verbose=False):
    """ Запуск указанной SAP системы \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    # with _sap_db():
    sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3) if mandant else '',
                            str(user).upper() if user else '', '')
    result = sap.run(sap_system)

    if not result:
        utilities.no_result_output(str(system).upper(), str(mandant).zfill(3), user)

    cfg = sap.config.Config()
    _config = cfg.read()

    sapshcut_exe_path = _config.command_line_path
    if not os.path.exists(sapshcut_exe_path):
        click.echo(click.style('В INI файле не найден путь к sapshcut.exe \n', **utilities.color_warning))
        sys.exit()

    selected_system = utilities.choose_system(
        [Sap_system(item[0], item[1], item[2], Crypto.decrypto(item[3])) for item in result], verbose)

    # Добавляем параметры для запуска SAP системы
    argument = [
        sapshcut_exe_path,  # Путь до sapshcut.exe
        f"-system={selected_system.system}",  # Id системы
        f"-client={str.zfill(selected_system.mandant, 3)}",  # Номер манданта
        f"-user={user}" if user else f"-user={selected_system.user}",  # Пользователь
        f"-pw={password}" if password else f"-pw={selected_system.password}",  # Пароль
        f"-language={language}",  # Язык для входа
        '-maxgui',  # Развернуть окно на весь экран
    ]

    return argument
