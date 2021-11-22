#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import os
import subprocess
import time
import ctypes
import sys
import getpass
from contextlib import contextmanager
import pyperclip
import click
import sap.config
from sap.api import Sap_system
from sap.crypto import Crypto
import sap.utilities as utilities
from sap.database import SapDB
from sap.config import create_config, open_config


@click.group()
@click.pass_context
def sap_cli(ctx):
    """Command line tool to launch SAP systems from saplogon application"""

    ctx.ensure_object(dict)

    cfg = sap.config.Config()
    _config = cfg.read()

    ctx.obj['CONFIG_DATA'] = _config
    ctx.obj['CONFIG_METHODS'] = cfg
    ctx.obj['CRYPTO'] = Crypto(_config.public_key_path, _config.private_key_path)
    ctx.obj['DATABASE'] = SapDB()


@sap_cli.command("logon")
@click.pass_context
def logon(ctx):
    """Launch SAPLogon application"""

    saplogon_exe_path = ctx.obj['CONFIG_DATA'].saplogon_path
    if not os.path.exists(saplogon_exe_path):
        raise utilities.WrongPath("saplogon.exe", saplogon_exe_path)

    click.launch(saplogon_exe_path)


@sap_cli.command("run")
@click.argument("system", type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="User id. Either user from database to narrow system selection "
                                           "if several users exist for one system, or user outside of the database",
              )
@click.option(
    "-eu", "--external_user", "external_user", help="Launch sap system with external user (outside database)",
    type=click.BOOL, default=False, is_flag=True,
)
@click.option("-l", "--language", "language", help="Language to logon", default="RU")
@click.option("-t", "--transaction", "transaction", help="Transaction to start after loggin on to SAP system", )
@click.option("-p", "--parameter", "parameter", help="Transaction's parameters")
@click.pass_context
def run(ctx, system: str, mandant: int, user: str, external_user: bool, language: str, transaction: str,
        parameter: str, ):
    """
    Launch SAP system \n
    Required arguments : \n
    1. SYSTEM - system id from saplogon

    Optional arguments: \n
    2. MANDANT - mandant or client id of sap system
    """
    password = ""
    _result = []

    if external_user:

        if not mandant:
            mandant = input("Enter mandant: ")
        user = input("Enter external user id: ")
        password = getpass.getpass("Enter password for external user: ")

        result = [(system.upper(), str(mandant).zfill(3), user.upper(), password, "", "")]
    else:
        with _sap_db(ctx.obj['CONFIG_DATA']):
            sap_system_sql = Sap_system(
                system.upper(),
                str(mandant).zfill(3) if mandant else None,
                user.upper() if user else None,
            )
            result = sap.query_system(sap_system_sql)

        if not result:
            sap_system_output = utilities.sap_systems_list_into_nametuple(
                [
                    [
                        system.upper(),
                        str(mandant).zfill(3) if mandant else None,
                        user.upper() if user else None,
                        None,
                        None,
                        None,
                    ]
                ]
            )

            utilities.print_system_list(
                sap_system_output,
                "NOTHING FOUND according to search criteria",
                color=utilities.color_warning,
            )
            sys.exit()

    for item in result:
        pwd = ctx.obj['CRYPTO'].decrypto(item[3])
        _result.append((item[0], item[1], item[2], pwd, item[4], item[5]))

    argument, selected_system = utilities.prepare_parameters_to_launch_system(_result, password, language, user, "",
                                                                              ctx.obj['CONFIG_DATA'].command_line_path)

    if transaction:
        item = "-type=transaction"
        argument.append(item)

        if parameter:
            # TODO: Доделать запуск транзакции с параметрами

            # param_data = sap.query_param(str(transaction).upper())

            # item = f"-command=\"*{transaction.upper()} {param_data[0][1]}={parameter}\""
            # item = '-command=\"*TM_52 VTGFHA-BUKRS=TRM1; VTGFHA-RFHA=100000000057;\"'
            item = '-command="/n*FBM1 BKPF-BUKRS=1000;"'
            argument.append(item)

            print(item)
        else:
            item = "-command=" + transaction
            argument.append(item)

    if external_user:
        message = "Trying to LAUNCH the following system with EXTERNAL USERS"
    else:
        message = "Trying to LAUNCH the following system"
    utilities.print_system_list(selected_system, message, transaction=transaction)

    # Запускаем SAP
    ret = subprocess.call(argument)

    if ret:
        click.echo(ret)


@sap_cli.command("debug")
@click.argument("system", required=False, type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="User")
@click.option("-pw", "--password", "password", help="Password")
@click.option("-l", "--language", "language", help="Logon language", default="RU")
@click.option("-f", "--file", "file", help="Create debug file", is_flag=True, type=click.BOOL)
@click.pass_context
def debug(ctx, system, mandant="", user="", password="", language="RU", file=False):
    """
    System debug \n
    You can: \n
    1. Creat debug file - to debug modal dialog box: SAP DEBUG -f \n
    2. Start debuggin of the opened system (the last used windows will be used): SAP DEBUG <SYSTEM> <MANDANT> \n

    Optional arguments: \n
    1. SYSTEM - system id from saplogon \n
    2. MANDANT - mandant or client id of sap system \n
    """
    _result = []

    if file:
        file_name = "DEBUG.TXT"

        click.echo(f"\n{file_name} file will be created.")
        click.echo(f"After creation, a folder with {file_name} file will be opened \n")
        click.echo("Drag the file to the SAP system to start debug mode \n")
        click.pause("Press Enter to continue")

        path = utilities.path()
        file_path = path + "\\" + file_name
        with open(file_path, "w") as writer:
            writer.write("[FUNCTION]\n")
            writer.write("Command =/H\n")
            writer.write("Title=Debugger\n")
            writer.write("Type=SystemCommand")

        command = f"explorer /select, {file_path}"
        subprocess.Popen(command)

    else:
        with _sap_db(ctx.obj['CONFIG_DATA']):
            sap_system_sql = Sap_system(
                str(system).upper(),
                str(mandant).zfill(3) if mandant else None,
                str(user).upper() if user else None,
            )
            result = sap.query_system(sap_system_sql)

            if not result:
                sap_system_output = utilities.sap_systems_list_into_nametuple(
                    [
                        [
                            str(system).upper(),
                            str(mandant).zfill(3) if mandant else "",
                            str(user).upper() if user else "",
                            "",
                            "",
                            "",
                        ]
                    ]
                )
                utilities.print_system_list(
                    sap_system_output,
                    "NOTHING FOUND according to search criteria",
                    color=utilities.color_warning,
                )
            else:

                for item in result:
                    pwd = ctx.obj['CRYPTO'].decrypto(item[3])
                    _result.append((item[0], item[1], item[2], pwd, item[4], item[5]))

                argument, selected_system = prepare_parameters_to_launch_system(_result, password, language, user, "",
                                                                                ctx.obj[
                                                                                    'CONFIG_DATA'].command_line_path)

                item = "-command=/H"
                argument.append(item)
                item = "-type=SystemCommand"
                argument.append(item)

                utilities.print_system_list(selected_system, "Trying to DEBUG the following system")

                ret = subprocess.call(argument)


@sap_cli.command("pw")
@click.argument("system", type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.pass_context
def pw(ctx, system, mandant):
    """
    Copy password for the requested system into clipboard.
    Script waits 15 seconds and clears clipboard.

    Required arguments: \n
    1. SYSTEM ID - system id from saplogon \n \n

    Optional argument: \n
    2. MANDANT - mandant or client id of sap system \n
    """
    _result = []

    with _sap_db(ctx.obj['CONFIG_DATA']):
        timeout = 15

        sap_system_sql = Sap_system(str(system).upper(), str(mandant).upper() if mandant else None)
        result = sap.query_system(sap_system_sql)

        if not result:
            sap_system_output = utilities.sap_systems_list_into_nametuple(
                [
                    [
                        str(system).upper(),
                        str(mandant).upper() if mandant else "",
                        "",
                        "",
                        "",
                        "",
                    ]
                ]
            )
            utilities.print_system_list(
                sap_system_output,
                "NOTHING FOUND according to search criteria",
                color=utilities.color_warning,
            )
        else:

            for item in result:
                pwd = ctx.obj['CRYPTO'].decrypto(item[3])
                _result.append((item[0], item[1], item[2], pwd, item[4], item[5]))

            sap_system_output = utilities.sap_systems_list_into_nametuple(_result)
            selected_system = utilities.choose_system(sap_system_output)

            pyperclip.copy(selected_system.password[0])

            click.echo(
                click.style(
                    f"Password is copied into clipboard.\nClipboard will be cleared in {timeout} seconds.\n",
                    **utilities.color_message,
                )
            )
            click.echo(
                click.style(
                    "If you use Clipboard manager, you should add PY.EXE, CMD.EXE applications to the exclusion list,\n"
                    "in order to keep sensitive information safe.",
                    **utilities.color_sensitive,
                )
            )

            time.sleep(timeout)
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()

            click.echo(click.style("\nClipboard is cleared. \n", **utilities.color_success))


@sap_cli.command("add")
@click.option("-system", prompt=True, help="System", type=utilities.LETTERS_NUMBERS_3)
@click.option("-mandant", prompt=True, help="Client", type=click.IntRange(1, 999))
@click.option("-user", prompt=True, help="User")
@click.option("-password", help="Password", prompt=True, confirmation_prompt=True, hide_input=True)
@click.option("-customer", prompt=True, help="Customer", type=click.STRING)
@click.option("-description", prompt=True, help="Description", type=click.STRING)
@click.pass_context
def add(ctx, system, mandant, user, password, description, customer):
    """
    Add sap system with it's parameters to db.

    Just run SAP ADD and enter system parameters
    """
    _result = []

    with _sap_db(ctx.obj['CONFIG_DATA']):
        encrypted_password = ctx.obj['CRYPTO'].encrypto(str.encode(password))
        sap_system = Sap_system(
            str(system).upper(),
            str(mandant).zfill(3),
            str(user).upper(),
            encrypted_password,
            str(customer).upper(),
            str(description),
        )
        result = sap.add(sap_system)

        if result is not None:
            click.echo(
                click.style(
                    "Failed to add system to database ... \n",
                    **utilities.color_sensitive,
                )
            )
            click.echo(result)
        else:
            sap_system = Sap_system(str(system).upper() if system else None, str(mandant) if mandant else None)
            result = sap.query_system(sap_system)

            for item in result:
                pwd = ctx.obj['CRYPTO'].decrypto(item[3])
                _result.append((item[0], item[1], item[2], pwd, item[4], item[5]))

            sap_system = utilities.sap_systems_list_into_nametuple(_result)
            utilities.print_system_list(sap_system, "The following system is ADDED to the database: ")


@sap_cli.command("update")
@click.option("-system", prompt=True, help="System", type=utilities.LETTERS_NUMBERS_3)
@click.option("-mandant", prompt=True, help="Mandant", type=click.IntRange(1, 999))
@click.option("-user", prompt=True, help="User")
@click.option("-password", help="Password", prompt=True, confirmation_prompt=True, hide_input=True)
@click.option("-customer", prompt=True, help="Customer", type=click.STRING)
@click.option("-description", prompt=True, help="System description", type=click.STRING)
@click.pass_context
def update(ctx, system, mandant, user, password, customer, description):
    """
    Update selected records of database

    Just run SAP UPDATE and enter system parameters to update
    """

    # TODO: вставлять данные уже сущетсвующей системы, чтобы пользователь мог
    #  решить, что изменять и изменять, или не изменять.
    _result = []

    encrypted_password = ctx.obj['CRYPTO'].encrypto(str.encode(password))
    sap_system_sql = Sap_system(
        str(system).upper(),
        str(mandant).zfill(3),
        str(user).upper(),
        password,
        str(customer),
        str(description),
    )
    sap_encrypted_system = Sap_system(
        str(system).upper(),
        str(mandant).zfill(3),
        str(user).upper(),
        encrypted_password,
        str(customer),
        str(description),
    )

    with _sap_db(ctx.obj['CONFIG_DATA']):
        result = sap.update(sap_encrypted_system)

        if result is None:
            result = sap.query_system(sap_system_sql)

            for item in result:
                pwd = ctx.obj['CRYPTO'].decrypto(item[3])
                _result = [(item[0], item[1], item[2], pwd, item[4], item[5])]

            sap_system_output = utilities.sap_systems_list_into_nametuple(_result)

            utilities.print_system_list(sap_system_output, "The following system is UPDATED", verbose=True)
            click.pause("Press Enter. Information about passwords will be deleted from screen ...")
            os.system("cls")
        else:
            sap_system_output = utilities.sap_systems_list_into_nametuple(
                [
                    [
                        str(system).upper(),
                        str(mandant).zfill(3) if mandant else "",
                        str(user).upper() if user else "",
                        "",
                        "",
                        "",
                    ]
                ]
            )
            utilities.print_system_list(
                sap_system_output,
                "FAILED TO UPDATE the following system",
                color=utilities.color_warning,
            )


@sap_cli.command("delete")
@click.option("-system", prompt=True, help="система", type=utilities.LETTERS_NUMBERS_3)
@click.option("-mandant", prompt=True, help="мандант", type=click.IntRange(1, 999))
@click.option("-user", prompt=True, help="пользователь")
@click.pass_context
def delete(ctx, system, mandant, user):
    """Удаление указанной SAP системы из базы данных"""
    mandant = int(str(mandant).zfill(3))
    sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper())

    with _sap_db(ctx.obj['CONFIG_DATA']):
        result = sap.delete(sap_system)

        result = sap.query_system(sap_system)

        if result == []:
            sap_system = utilities.sap_systems_list_into_nametuple(
                [
                    [
                        str(system).upper(),
                        str(mandant).zfill(3),
                        str(user).upper(),
                        "",
                        "",
                        "",
                    ]
                ]
            )
            utilities.print_system_list(sap_system, "The following system is DELETED from database")
        else:
            sap_system_output = utilities.sap_systems_list_into_nametuple(
                [
                    [
                        str(system).upper(),
                        str(mandant).zfill(3) if mandant else "",
                        str(user).upper() if user else "",
                        "",
                        "",
                        "",
                    ]
                ]
            )
            utilities.print_system_list(
                sap_system_output,
                "FAILED TO UPDATE the following system",
                color=utilities.color_warning,
            )


@sap_cli.command("config")
@click.option('-create', is_flag=True, callback=create_config, expose_value=False,
              is_eager=True,
              help='Create config file')
@click.option('-open', is_flag=True, callback=open_config, expose_value=False,
              is_eager=True,
              help='Open config file')
@click.pass_context
def config(ctx):
    """Создание конфигурационного ini файла"""

    click.echo("Enter one of subcommands:")
    click.echo("\t -create - Create config file")
    click.echo("\t -open   - Open config file")


@sap_cli.command("list")
@click.argument("system", required=False, type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-v", "--verbose", "verbose", help="Show password", is_flag=True)
@click.pass_context
def list_systems(ctx, system, mandant, verbose):
    """
    Print information about system(s)

    Optional arguments: \n
    1. System: System Id \n
    2. Mandant: Mandant num \n

    If no arguments - print info about all systems
    """
    _result = []

    with _sap_db(ctx.obj['CONFIG_DATA']):
        sap_system = Sap_system(str(system).upper() if system else None, str(mandant) if mandant else None)
        result = sap.query_system(sap_system)

        if not result:
            sap_system_output = utilities.sap_systems_list_into_nametuple(
                [
                    [
                        str(system).upper() if system else "",
                        str(mandant).zfill(3) if mandant else "",
                        "",
                        "",
                        "",
                        "",
                    ]
                ]
            )
            utilities.print_system_list(
                sap_system_output,
                "NOTHING FOUND according to search criteria",
                color=utilities.color_warning,
            )
        else:
            for item in result:
                pwd = ctx.obj['CRYPTO'].decrypto(item[3])
                _result.append((item[0], item[1], item[2], pwd, item[4], item[5]))

            sap_system = utilities.sap_systems_list_into_nametuple(_result)

            utilities.print_system_list(sap_system, "Available systems", verbose=verbose)
            if verbose:
                click.pause("Press Enter. Information about passwords will be deleted from screen ...")
                os.system("cls")
            else:
                pass


@sap_cli.command("db")
@click.pass_context
def database(ctx):
    """Создание базы данных для хранеия информкции о SAP системах"""
    pass
    # db = Database()
    # db.create()


@sap_cli.command("keys")
@click.pass_context
def keys(ctx):
    """ Создание ключей шифрования """
    ctx.obj['CRYPTO'].generate_keys()


@sap_cli.command("ver", help="Текущая версия SAP shortcut")
@click.pass_context
def shortcut_version(ctx):
    # Считываем конфигурационный файл
    parameter = "-version"
    utilities.launch_command_line_with_params(ctx.obj['CONFIG_DATA'].command_line_path, parameter)


@sap_cli.command("help", help="SAP GUI shortcut help")
@click.pass_context
def shortcut_help(ctx):
    # Считываем конфигурационный файл
    utilities.launch_command_line_with_params(ctx.obj['CONFIG_DATA'].command_line_path, "-help")


@sap_cli.command("start")
@click.pass_context
def start(ctx):
    """
    Starting point for working wiht SAP command line tool
    1. Database creation.
    2. ini file with config parameters createion.
    3. Usefull messages
    """

    # TODO: Убрать вывод сообщения из классов базы данных, конфига и ключей шифрования и добавить сюда
    #   https://towardsdatascience.com/rich-generate-rich-and-beautiful-text-in-the-terminal-with-python-541f39abf32e

    ctx.obj['CONFIG_METHODS'].create()
    ctx.obj['CRYPTO'].generate_keys()
    ctx.obj['DATABASE'].create()

    click.launch(ctx.obj['CONFIG_DATA'].config_file_path)

    click.echo(
        click.style(
            "Ключи шифрования созданы:"
            f"{ctx.obj['CONFIG_DATA'].public_key_file_name}"
            f"{ctx.obj['CONFIG_DATA'].private_key_file_name}",
            **utilities.color_success,
        )
    )
    click.echo("Необходимо указать их расположение в файле *.ini")
    click.echo(
        click.style(
            f"Файл {ctx.obj['CONFIG_DATA'].private_key_file_name} должен находиться в зашифрованном хранилище",
            **utilities.color_sensitive,
        )
    )

    click.echo(click.style(f"База данных создана: {db.database_path}", **utilities.color_success))

    click.echo("Путь: %s \n" % click.format_filename(cfg.config_file_path))
    click.echo(click.style("INI файл создан", **utilities.color_success))
    click.echo(
        click.style(
            "!!! Заполните все требуемые параметры в файле !!! \n",
            **utilities.color_message,
        )
    )

    command = f"explorer /select, {utilities.path()}"
    subprocess.Popen(command)


@sap_cli.command("backup")
@click.pass_context
def backup(ctx):
    """
    Create back of \n
    1. saplogon systems (saplogon.ini. *.xml)
    2. password database
    3. cypher files
    4. config. ini
    """
    # TODO: создать команду для бэкапа ini, xml фалов с системами sap
    #  также бэкапить базу данных, ключи шифрования, ini конфигурационных файлов
    #  Создавать zip архив с паролем
    #  Пути к saplogon.ini брать отсюда 2580439
    pass


@sap_cli.command("launch")
@click.argument("system", type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="пользователь")
@click.option("-pw", "--password", "password", help="пароль")
@click.option("-l", "--language", "language", help="язык входа", default="RU")
@click.option("-t", "--transaction", "transaction", help="код транзакции")
@click.option("-p", "--parameter", "parameter", help="параметры для транзакции")
@click.pass_context
def launch(ctx,
           system,
           mandant="",
           user="",
           password="",
           language="RU",
           transaction="",
           parameter="",
           ):
    """Launch sap system in web"""

    # TODO: сделать таблицу https ардесов для SAP системы,
    # путь до браузера, чтобы запускать их в браузере.
    pass


@contextmanager
def _sap_db(cfg):
    sap.start_sap_db(cfg.db_path, cfg.db_type)
    yield
    sap.stop_sap_db()


if __name__ == "__main__":
    sys.excepthook = utilities.show_exception_and_exit
    # sys.tracebacklimit = 0  # Stop printing traceback. Only messages for exceptions.
    sap_cli(obj={})
