#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import click
import sys
import traceback
import os
import subprocess
import operator
import re
from appdirs import *
from sap.api import Sap_system
from prettytable import PrettyTable
from operator import attrgetter
import winreg

# Цвета сообщений
color_message = {'bg': 'black', 'fg': 'white'}
color_success = {'bg': 'black', 'fg': 'green'}
color_warning = {'bg': 'black', 'fg': 'yellow'}
color_sensitive = {'bg': 'red', 'fg': 'white'}


def prepare_parameters_to_launch_system(result: list, password, language, user, transaction="",
                                        sapshcut_exe_path: str = ""):
    # cfg = sap.config.Config()
    # _config = cfg.read()
    # sapshcut_exe_path = _config.command_line_path

    if not os.path.exists(sapshcut_exe_path):
        raise utilities.WrongPath("sapshcut.exe", sapshcut_exe_path)

    sap_system_output = sap_systems_list_into_nametuple(result)
    selected_system = choose_system(sap_system_output)

    # Добавляем параметры для запуска SAP системы
    argument = [
        sapshcut_exe_path,  # Путь до sapshcut.exe
        f"-system={selected_system.system[0]}",  # Id системы
        f"-client={str(selected_system.mandant[0]).zfill(3)}",  # Номер манданта
        f"-user={user}" if user else f"-user={selected_system.user[0]}",  # Пользователь
        f"-pw={password}" if password else f"-pw={selected_system.password[0]}",  # Пароль
        f"-language={language}",  # Язык для входа
        "-maxgui",  # Развернуть окно на весь экран
    ]
    return argument, selected_system


def sap_systems_list_into_nametuple(result: list) -> Sap_system:
    systems = [item[0] for item in result]
    mandants = [item[1] for item in result]
    users = [item[2] for item in result]
    passwords = [item[3] for item in result]
    customers = [item[4] for item in result]
    descriptions = [item[5] for item in result]

    sap_system = Sap_system(systems, mandants, users, passwords, customers, descriptions)

    return sap_system


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


class String_3(click.ParamType):
    """Click check class for parameters type"""

    name = "Only letters and numbers. 3 chars length"

    def convert(self, value, param, ctx):
        if re.match("^[A-Za-z0-9]*$", value) and len(value) == 3:
            return value

        self.fail(
            f"{value!r} is not valid [SYSTEM] id. Must contain only letters and numbers. Must be 3 chars length",
            param,
            ctx,
        )


LETTERS_NUMBERS_3 = String_3()


class Pass_requirement(click.ParamType):
    """Click check class for parameters type"""

    # TODO: долать требования к паролю, чтобы он был не простым

    name = "Requirements for password"

    def convert(self, value, param, ctx):
        if re.match("^[A-Za-z0-9]*$", value):
            return value

        self.fail(
            f"{value!r} Password is week. Use xxxxxx chars",
            param,
            ctx,
        )


PASS_REQUIREMENT = Pass_requirement()


def get_reg(name):
    REG_PATH = r"Software\SAP\SAPLogon\Options"

    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                      winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None
