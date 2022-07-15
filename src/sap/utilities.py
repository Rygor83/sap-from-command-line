#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" helpful functions """

import click
from pathlib import Path
from subprocess import Popen
import re
import time
import getpass
import pyautogui

import sap.api
import sap.config
from sap.api import Sap_system, Parameter
from sap.exceptions import WrongPath

from rich.markdown import Markdown
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text
from rich.prompt import IntPrompt

from rich_click.rich_click import (
    ALIGN_ERRORS_PANEL,
    STYLE_ERRORS_PANEL_BORDER,
    STYLE_USAGE,
    STYLE_SWITCH,
)

# Цвета сообщений
color_message = {'bg': 'black', 'fg': 'white'}
color_success = {'bg': 'black', 'fg': 'green'}
color_warning = {'bg': 'black', 'fg': 'yellow'}
color_sensitive = {'bg': 'red', 'fg': 'white'}

message_type_message = "Message"
message_type_warning = "Warning"
message_type_sensitive = "Sensitive"
message_type_error = "Error"


def prepare_parameters_to_launch_system(selected_system: Sap_system, language, external_user, guiparm, snc_name,
                                        snc_qop, transaction='', parameter='', report='', system_command='', reuse='',
                                        sapshcut_exe_path: str = ""):
    """
    Constructing a string to start the system
    :param selected_system:
    :param language:
    :param external_user:
    :param guiparm:
    :param snc_name:
    :param snc_qop:
    :param transaction:
    :param parameter:
    :param report:
    :param system_command:
    :param sapshcut_exe_path:
    :return:
    """

    # TODO: переделать, чтобы у нужных параметров были дефолтные значения, а это будет означать, что можно
    # не передавать параметры при вызове - а значит нужно будет убрать множество None

    try:
        check_if_path_exists(sapshcut_exe_path)
    except WrongPath as err:
        print_message(f"{err}", message_type=message_type_error)
        raise click.Abort

    argument: str = ""
    argument = argument + f'"{sapshcut_exe_path}"'  # Путь до sapshcut.exe
    argument = argument + f" -system={selected_system.system}"  # Id системы
    argument = argument + f" -client={str(selected_system.mandant).zfill(3)}"  # Номер манданта

    if external_user:
        user = input("\nEnter external user id: ")
        argument = argument + f" -user={user}"  # Пользователь
    else:
        argument = argument + f" -user={selected_system.user}"  # Пользователь

    if external_user:
        password = getpass.getpass("Enter password for external user: ")
        argument = argument + f" -pw={password}"  # Пароль
    else:
        argument = argument + f" -pw={selected_system.password}"  # Пароль

    argument = argument + f" -language={language}"  # Язык для входа

    if guiparm:
        argument = argument + f" -guiparm={guiparm}"  #

    if snc_name:
        argument = argument + f" -snc_name={snc_name}"  #

    if snc_qop:
        argument = argument + f" -snc_qop={snc_qop}"  #

    argument = argument + " -maxgui"  # Развернуть окно на весь экран

    if external_user:
        edited_system = Sap_system(selected_system.system, selected_system.mandant, str(user).upper(), password,
                                   selected_system.customer, selected_system.description, selected_system.url,
                                   selected_system.autotype)
    else:
        edited_system = selected_system

    if transaction:
        command = transaction
        command_type = 'transaction'

        argument += " -type=transaction"

        if parameter:
            param = Parameter(str(transaction).upper(), None)
            param_data = sap.query_param(param)

            if param_data:
                command += f" -> {parameter}"
                param_list = param_data[0][1].split(',')
                param_value = parameter.split(',')

                param_list_value = zip(param_list, param_value)

                argument += f' -command="*{transaction.upper()}'
                for item in param_list_value:
                    argument += f' {item[0]}={item[1]};'
                argument += '"'
            else:
                print_message(f"\nThere is no parameter info for {transaction.upper()} transaction",
                              message_type=message_type_warning)

                argument += f' -command="{transaction.upper()}"'
        else:
            argument = argument + " -command=" + transaction
    elif system_command:
        command = system_command
        command_type = 'system command'

        argument += " -type=SystemCommand"
        argument += " -command=" + system_command

    elif report:
        command = report
        command_type = 'report'

        argument += " -type=report"
        argument += " -command=" + report
    else:
        command = None
        command_type = None

    if reuse:
        argument += ' -reuse=0'
    else:
        argument += ' -reuse=1'

    return argument, edited_system, command, command_type


def launch_command_line_with_params(command_line_path, param):
    """ Запуск sapshcut.exe с разными параметрами"""
    if not command_line_path.exists():
        raise WrongPath('sapshcut.exe', command_line_path)

    # Добавляем путь к командному файлу
    argument = [command_line_path, param]

    # Запускаем SAP
    pop = Popen(argument)
    pop.wait()

    if pop.returncode:
        click.echo(pop.returncode, pop.communicate()[0])


def launch_saplogon_with_params(saplogon):
    """ Запуск sapshcut.exe с разными параметрами"""

    try:
        check_if_path_exists(saplogon)
    except WrongPath as err:
        print_message(f"{err}", message_type_error)
        raise click.Abort
    else:
        click.echo(f'Trying to launch: {saplogon}')

    click.launch(url=str(saplogon))


def choose_system(sap_systems: list) -> Sap_system:
    ans = 0
    if len(sap_systems) >= 2:

        while int(ans) > len(sap_systems) or int(ans) < 1:
            if 1 <= int(ans) <= len(sap_systems):
                break

            click.echo()
            ans = IntPrompt.ask(
                f"\n[bold red]Choose a system you want to login.[/bold red] Available values from 1 to {str(len(sap_systems))}: \n>>>")
        ans = ans - 1

    selected_system: Sap_system = Sap_system(
        sap_systems[ans].system, sap_systems[ans].mandant, sap_systems[ans].user, sap_systems[ans].password,
        sap_systems[ans].customer, sap_systems[ans].description, sap_systems[ans].url, sap_systems[ans].autotype)

    return selected_system


def choose_parameter(parameters: list):
    ans = 0
    if len(parameters) >= 2:

        while int(ans) > len(parameters) or int(ans) < 1:
            if 1 <= int(ans) <= len(parameters):
                break

            click.echo()
            ans = IntPrompt.ask(
                f"\n[bold red]Choose a transaction with parameter.[/bold red] Available values from 1 to {str(len(parameters))}: \n>>>")
        ans = ans - 1

    selected_params = Parameter(parameters[ans].transaction, parameters[ans].parameter)

    return selected_params


def print_system_list(*sap_systems: Sap_system, title, color=color_success, verbose=False, timeout=0,
                      enum=False, command: str = '', command_type: str = '', url=False):
    """ Print information in table style """

    row = []

    # Title
    title = f"{click.style(title, **color)}"
    if command:
        title = title + click.style(f"with {command_type} ", **color)
        title = title + click.style(f"{str(command).upper()}", **color_sensitive)

    # Table initializing
    table = Table(title=title, box=box.SQUARE_DOUBLE_HEAD, expand=True)

    # Header
    if enum:
        header = ['Id', 'Customer', 'System', 'Mandant', 'Description', 'User']
    else:
        header = ['Customer', 'System', 'Mandant', 'Description', 'User']
    if url:
        header.append('URL')
        header.append('Autotype sequence')
    if verbose:
        header.append('Password')

    for item in header:
        table.add_column(item)

    # Rows
    for index, sap_system in enumerate(sap_systems, start=1):
        if enum:
            row.append(str(index))
        if sap_system.customer is not None:
            row.append(sap_system.customer)
        else:
            row.append('')

        if sap_system.system is not None:
            row.append(sap_system.system)
        else:
            row.append('')

        if sap_system.mandant is not None:
            row.append(sap_system.mandant)
        else:
            row.append('')

        if sap_system.description is not None:
            row.append(sap_system.description)
        else:
            row.append('')

        if sap_system.user is not None:
            row.append(sap_system.user)
        else:
            row.append('')

        if url:
            if sap_system.url is not None:
                row.append(sap_system.url)
                row.append(sap_system.autotype)
            else:
                row.append('')
                row.append('')

        if verbose and sap_system.password is not None:
            row.append(sap_system.password)

        table.add_row(*row)
        row.clear()

    # Information output
    click.echo('\n')
    console = Console()
    console.print(table)

    if verbose:
        print_message(
            f"Information about passwords will be deleted from screen in {timeout}", message_type_message)
        try:
            countdown(timeout)
        except KeyboardInterrupt:
            print_message("Aborted!", message_type_error)
        click.clear()


def print_parameters_list(*parameters: Parameter, title, color=color_success, enum=False):
    """ Print information in table style """

    row = []

    # Title
    title = f"{click.style(title, **color)}"

    # Table initializing
    table = Table(title=title, box=box.SQUARE_DOUBLE_HEAD, expand=True)

    # Header
    if enum:
        header = ['Id', 'Transaction', 'Parameters']
    else:
        header = ['Transaction', 'Parameters']

    for item in header:
        table.add_column(item)

    # Rows
    for index, parameter in enumerate(parameters, start=1):
        if enum:
            row.append(str(index))

        if parameter.transaction is not None:
            row.append(parameter.transaction)
        else:
            row.append('')

        if parameter.parameter is not None:
            row.append(parameter.parameter)
        else:
            row.append('')

        table.add_row(*row)
        row.clear()

    # Information output
    click.echo('\n')
    console = Console()
    console.print(table)


def path():
    return Path(click.get_app_dir('sap', roaming=False))


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

    # TODO: доделать требования к паролю, чтобы он был не простым

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


def countdown(seconds):
    for i in range(seconds, -1, -1):
        # move to the beginning of the line and remove line
        print("\r\033[K", end='', flush=True)
        print(f"\r{i}", end='', flush=True)
        time.sleep(1)


def print_message(message, message_type):
    console = Console()

    if message_type == message_type_error:
        border_style = STYLE_ERRORS_PANEL_BORDER
        title_align = ALIGN_ERRORS_PANEL
    elif message_type == message_type_warning:
        border_style = STYLE_USAGE
        title_align = ALIGN_ERRORS_PANEL
    elif message_type == message_type_sensitive:
        border_style = 'bold red'
        title_align = ALIGN_ERRORS_PANEL
    elif message_type == message_type_message:
        border_style = STYLE_SWITCH
        title_align = ALIGN_ERRORS_PANEL

    console.print(Panel(
        Text.from_markup(message),
        border_style=border_style,
        title=message_type,
        title_align=title_align)
    )


def print_markdown(markdown):
    console = Console()
    md = Markdown(markdown)
    console.print(md)


def default_sequence():
    """
    Default values from configuration file for CLICK.OPTION for [AUTO-TYPE]->sequence
    """
    config = sap.config.Config()
    try:
        _config = config.read()
    except:
        return ""

    return _config.sequence


def default_time_to_clear():
    """
    Default values from configuration file for CLICK.OPTION for [PASSWORD]->time_to_clear
    """
    config = sap.config.Config()
    try:
        _config = config.read()
    except:
        return ""

    return _config.time_to_clear


def default_time_to_wait_for_web():
    """
    Default values from configuration file for CLICK.OPTION for [AUTO-TYPE]->wait
    """
    config = ""
    config = sap.config.Config()
    try:
        _config = config.read()
    except:
        return ""

    return _config.wait_site_to_load


def open_sap(argument):
    pop = Popen(argument)
    pop.wait()

    if pop.returncode:
        click.echo(pop.returncode, pop.communicate()[0])


def check_if_path_exists(path):
    if not path.exists():
        raise WrongPath(path.name, path)
    return True


def launch_autotype_sequence(autotype, user, password):
    """
    Entering data according autotype sequence at website

    :param autotype: autotype sequence
    :param user: user id
    :param password: user's password
    :return: None
    """
    key_strokes = re.findall(r'{(.+?)}', autotype)

    for item in key_strokes:
        if item == 'USER':
            pyautogui.write(str(user))
        elif item == 'PASS':
            pyautogui.write(str(password))
        else:
            pyautogui.press(item)


def open_url(url, locate=False):
    """ Open url in web browser"""
    click.launch(url=url, locate=locate)
