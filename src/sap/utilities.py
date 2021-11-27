#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
import typing
import click
import sys
import traceback
import os
from subprocess import call
import operator
import re
from prettytable import PrettyTable
from operator import attrgetter
import winreg
import time

import sap.api
from sap.api import Sap_system

# Цвета сообщений
color_message = {'bg': 'black', 'fg': 'white'}
color_success = {'bg': 'black', 'fg': 'green'}
color_warning = {'bg': 'black', 'fg': 'yellow'}
color_sensitive = {'bg': 'red', 'fg': 'white'}


def prepare_parameters_to_launch_system(selected_sap_systems: list, password, language, user, transaction="",
                                        sapshcut_exe_path: str = "") -> typing.Tuple[list, Sap_system]:
    # cfg = sap.config.Config()
    # _config = cfg.read()
    # sapshcut_exe_path = _config.command_line_path

    # if not os.path.exists(sapshcut_exe_path):
    #     raise exceptions.WrongPath("sapshcut.exe", sapshcut_exe_path)

    # sap_system_output = sap_systems_list_into_nametuple(result)
    selected_system: Sap_system = choose_system(selected_sap_systems)

    # Добавляем параметры для запуска SAP системы
    argument = [
        sapshcut_exe_path,  # Путь до sapshcut.exe
        f"-system={selected_system.system}",  # Id системы
        f"-client={str(selected_system.mandant).zfill(3)}",  # Номер манданта
        f"-user={user}" if user else f"-user={selected_system.user}",  # Пользователь
        f"-pw={password}" if password else f"-pw={selected_system.password}",  # Пароль
        f"-language={language}",  # Язык для входа
        "-maxgui",  # Развернуть окно на весь экран
    ]
    return argument, selected_system


def launch_command_line_with_params(command_line_path, param):
    ''' Запуск sapshcut.exe с разными параметрами'''
    if not os.path.exists(command_line_path):
        raise utilities.WrongPath('sapshcut.exe', command_line_path)

    # Добавляем путь к командному файлу
    argument = [command_line_path, param]

    # Запускаем SAP
    call(argument)


def choose_system(sap_systems: list, verbose=False) -> Sap_system:
    ans = 0
    if len(sap_systems) >= 2:
        # print_system_list(sap_systems, 'Available systems', verbose=verbose, enum=True)

        while int(ans) > len(sap_systems) or int(ans) < 1:
            if 1 <= int(ans) <= len(sap_systems):
                break

            click.echo()
            ans = click.prompt(click.style(
                f"\nChoose system you want to logon. Available values from 1 to {str(len(sap_systems))}: \n>>>",
                **color_message), type=int)
        ans = ans - 1

    selected_system: Sap_system = Sap_system(
        sap_systems[ans].system, sap_systems[ans].mandant, sap_systems[ans].user, sap_systems[ans].password,
        sap_systems[ans].customer, sap_systems[ans].description, sap_systems[ans].url)

    return selected_system


def print_system_list(sap_systems, title, color=color_success, verbose=False,
                      enum=False, transaction: str = '', url=False):
    # TODO: доделать формирование list(Sap_system) внутри этой подпрограммы

    if type(sap_systems) is Sap_system:
        sap_systems = [sap_systems]

    row = []

    # Header for Pretty table
    if enum:
        header = ['Id', 'Customer', 'System', 'Mandant', 'Description', 'User']
    else:
        header = ['Customer', 'System', 'Mandant', 'Description', 'User']
    if url:
        header.append('URL')
    if verbose:
        header.append('Password')

    # Table with data
    t = PrettyTable(header)

    for index, sap_system in enumerate(sap_systems, start=1):
        if enum:
            row.append(index)
        if sap_system.customer is not None:
            row.append(sap_system.customer)
            t.align["Customer"] = "l"
        else:
            row.append('')

        if sap_system.system is not None:
            row.append(sap_system.system)
            t.align["System"] = "l"
        else:
            row.append('')

        if sap_system.mandant is not None:
            row.append(sap_system.mandant)
            t.align["Mandant"] = "l"
        else:
            row.append('')

        if sap_system.description is not None:
            row.append(sap_system.description)
            t.align["Description"] = "l"
        else:
            row.append('')

        if sap_system.user is not None:
            row.append(sap_system.user)
            t.align["User"] = "l"
        else:
            row.append('')

        if url:
            if sap_system.url is not None:
                row.append(sap_system.url)
                t.align["URL"] = "l"
            else:
                row.append('')

        if verbose and sap_system.password is not None:
            row.append(sap_system.password)
            t.align["Password"] = "l"

        t.add_row(row)
        row.clear()

    # Вывод информации
    click.echo('\n')
    title = f"{click.style(title, **color)}"
    if transaction:
        title = title + f"{click.style(' with transaction ', **color)}"
        title = title + f"{click.style(str(transaction).upper(), **color_sensitive)}"
    click.echo(t.get_string(title=title))


def show_exception_and_exit(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb)
    sys.exit(-1)


def path():
    return click.get_app_dir('sap', roaming=False)


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

    name = "Password"

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


def countdown(seconds):
    for i in range(seconds, -1, -1):
        # move to the beginning of the line and remove line
        print("\r\033[K", end='', flush=True)
        print(f"\r{i}", end='', flush=True)
        time.sleep(1)
