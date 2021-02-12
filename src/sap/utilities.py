#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import click
import sys
import traceback

from prettytable import PrettyTable
from operator import attrgetter
from sap.crypto import Crypto


def launch_command_line_with_params(command_line_path, param):
    if not os.path.exists(command_line_path):
        click.echo(
            click.style(f'Путь до sapshcut.exe не верный: \n{command_line_path} \n', bg='black', fg='yellow'))
        click.pause('Нажмите для продолжения ...')
        sys.exit()

    # Добавляем путь к командному файлу
    argument = [command_line_path, param]

    # Запускаем SAP
    subprocess.call(argument)


def print_system_list(systems: list, title, v=''):
    sorted_systems = sorted(systems, key=attrgetter('system', 'mandant'))

    # Формируем заголовок таблицы
    header = ['№', 'Система', 'Мандант', 'Пользователь']
    if v:
        header.append('Пароль')

    # Создаем таблицу
    t = PrettyTable(header)

    # Выравнивание
    t.align["Пользователь"] = "l"
    t.align["Пароль"] = "l"

    # Добавление информации в табилцу
    for num, system in enumerate(sorted_systems, start=1):
        row = [num, system.system, system.mandant, system.user]
        if v:
            row.append(Crypto.decrypto(system.password))
        t.add_row(row)

    # Вывод информации
    click.echo('\n')
    click.echo(t.get_string(title=click.style(title, bg='black', fg='green')))


def no_result_output(system, mandant='', user=''):
    click.echo(click.style(f'\nПо запрошенным данным системы в базе данных отсутствую:', bg='black', fg='green'))
    if system:
        click.echo(f'Система: {str(system).upper()}')
    if mandant:
        click.echo(f'Мандант: {mandant}')
    if user:
        click.echo(f'Пользователь: {str(user).upper()}')
    click.pause('\nНажмите для продолжения ...')
    sys.exit()


def show_exception_and_exit(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb)
    click.pause('Нажмите для продолжения ...')
    sys.exit(-1)
