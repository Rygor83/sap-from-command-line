#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import click
import sys
import traceback
import os
import subprocess
import operator

from appdirs import *
from sap.api import Sap_system
from prettytable import PrettyTable
from operator import attrgetter

# Цвета сообщений
color_message = {'bg': 'black', 'fg': 'white'}
color_success = {'bg': 'black', 'fg': 'green'}
color_warning = {'bg': 'black', 'fg': 'yellow'}
color_sensitive = {'bg': 'red', 'fg': 'white'}


def launch_command_line_with_params(command_line_path, param):
    ''' Запуск sapshcut.exe с разными параметрами'''
    if not os.path.exists(command_line_path):
        raise utilities.WrongPath('sapshcut.exe', command_line_path)

    # Добавляем путь к командному файлу
    argument = [command_line_path, param]

    # Запускаем SAP
    subprocess.call(argument)


def choose_system(sap_system: Sap_system, verbose=False):
    ans = 0
    if len(sap_system[0]) >= 2:
        print_system_list(sap_system, 'Available systems', verbose=verbose, enumerate=True)

        while int(ans) > len(sap_system[0]) or int(ans) < 1:
            if 1 <= int(ans) <= len(sap_system[0]):
                break
            click.echo(click.style(f"\nAvailable values from 1 to {str(len(sap_system[0]))}.", **color_message))
            ans = click.prompt('Choose system you want to logon \n>>>', type=int)
        ans = ans - 1

    system = Sap_system(
        [sap_system.system[ans]], [sap_system.mandant[ans]], [sap_system.user[ans]], [sap_system.password[ans]],
        [sap_system.customer[ans]], [sap_system.description[ans]])

    return system


def print_system_list(sap_system: Sap_system, title, color=color_success, verbose=False, enumerate=False,
                      transaction: str = ''):
    row = []

    # Header for Pretty table
    if enumerate:
        header = ['Id', 'Customer', 'System', 'Mandant', 'Description', 'User']
    else:
        header = ['Customer', 'System', 'Mandant', 'Description', 'User']
    if verbose:
        header.append('Password')

    # Table with data
    t = PrettyTable(header)

    for position in range(len(sap_system[0])):
        if enumerate:
            row.append(position + 1)
        if sap_system.customer[position] is not None:
            row.append(sap_system.customer[position])
            t.align["Customer"] = "l"
        else:
            row.append('')

        if sap_system.system[position] is not None:
            row.append(sap_system.system[position])
            t.align["System"] = "l"
        else:
            row.append('')

        if sap_system.mandant[position] is not None:
            row.append(sap_system.mandant[position])
            t.align["Mandant"] = "l"
        else:
            row.append('')

        if sap_system.description[position] is not None:
            row.append(sap_system.description[position])
            t.align["Description"] = "l"
        else:
            row.append('')

        if sap_system.user[position] is not None:
            row.append(sap_system.user[position])
            t.align["User"] = "l"
        else:
            row.append('')

        if verbose and sap_system.password[position] is not None:
            row.append(sap_system.password[position])
            t.align["Password"] = "l"

        t.add_row(row)
        row.clear()

    # Вывод информации
    click.echo('\n')
    title = f"{click.style(title, **color)}"
    if transaction:
        title = title + f"{click.style(' with transaction ', **color)}"
        title = title + f"{click.style(str(transaction).upper(), **color_sensitive)}"
    click.echo(t.get_string(title=title, sort_key=operator.itemgetter(1, 0), sortby="System"))
    click.echo('\n')


def show_exception_and_exit(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb)
    sys.exit(-1)


def path():
    return user_data_dir('sap', appauthor=False)


class WrongPath(Exception):
    """Base class for other exceptions"""

    def __init__(self, file, path, message="Wrong path to"):
        self.message = f'{message} {file} file: {path}'
        super().__init__(self.message)
