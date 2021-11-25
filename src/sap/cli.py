#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import os
from subprocess import call
import time
from datetime import datetime
import ctypes
import sys
import getpass
from contextlib import contextmanager
import pyperclip
import pyzipper
import click
import pathlib
import typing
from rich import print

import sap.config
from sap.api import Sap_system
from sap.crypto import Crypto
from sap import utilities
from sap.database import SapDB
from sap.config import create_config, open_config
from sap.file_names import CONFIG_NAME, DEBUG_FILE_NAME, PRIVATE_KEY_NAME, PUBLIC_KEY_NAME, DATABASE_NAME, \
    TIMER_TO_CLEAR_SCREEN


@click.group()
@click.pass_context
@click.option('-path', '--config_path', 'config_path', help="Path to external sap_config.ini folder", type=click.Path())
@click.version_option(version=sap.__version__)
def sap_cli(ctx, config_path: str):
    """Command line tool to launch SAP systems from saplogon application"""

    ctx.ensure_object(dict)

    if config_path:
        cfg = sap.config.Config(config_path)
    else:
        cfg = sap.config.Config()

    if cfg.exists():
        _config = cfg.read()
        ctx.obj['CONFIG_DATA'] = _config

    if _config:
        ctx.obj['CRYPTO'] = Crypto(_config.public_key_path, _config.private_key_path)
    else:
        ctx.obj['CRYPTO'] = Crypto(cfg.public_key_path, cfg.private_key_path)
    ctx.obj['DATABASE'] = SapDB()
    ctx.obj['DEBUG'] = config_path
    ctx.obj['CONFIG_METHODS'] = cfg


@sap_cli.command("logon")
@click.pass_context
def logon(ctx):
    """Launch SAPLogon application"""

    saplogon_exe_path = ctx.obj['CONFIG_DATA'].saplogon_path
    if not os.path.exists(saplogon_exe_path):
        raise utilities.WrongPath("saplogon.exe", saplogon_exe_path)

    click.launch(url=saplogon_exe_path)


@sap_cli.command("run")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="User id. Either user from database to narrow system selection "
                                           "if several users exist for one system, or user outside of the database",
              )
@click.option("-c", "--customer", "customer", help="Launch sap system by customer id", type=click.STRING)
@click.option("-d", "--description", "description", help="Launch sap system by customer id", type=click.STRING)
@click.option(
    "-eu", "--external_user", "external_user", help="Launch sap system with external user (outside database)",
    type=click.BOOL, default=False, is_flag=True,
)
@click.option("-l", "--language", "language", help="Language to logon", default="RU")
@click.option("-t", "--transaction", "transaction", help="Transaction to start after loggin on to SAP system", )
@click.option("-p", "--parameter", "parameter", help="Transaction's parameters")
@click.option("-w", "--web", "web", is_flag=True, help="Launch system web site")
@click.pass_context
def run(ctx, system: str, mandant: int, user: str, customer: str, description: str, external_user: bool, language: str,
        transaction: str, parameter: str, web: bool = False):
    """
    Launch SAP system \n

    Optional arguments: \n
    1. SYSTEM - system id from saplogon \n
    2. MANDANT - mandant or client id of sap system
    """
    password = ""

    if external_user:

        if not mandant:
            mandant = input("Enter mandant: ")
        user = input("Enter external user id: ")
        password = getpass.getpass("Enter password for external user: ")

        query_result = [Sap_system(system.upper(), str(mandant).zfill(3), user.upper(), password, "", "", "")]
    else:

        query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                                  description=description,
                                  url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        argument, selected_system = utilities.prepare_parameters_to_launch_system(selected_sap_systems, password,
                                                                                  language,
                                                                                  user, "",
                                                                                  ctx.obj[
                                                                                      'CONFIG_DATA'].command_line_path)

        if web:
            if selected_system.url != " ":
                # TODO: доделать передачу пароля для авторизации

                click.launch(url=f"{selected_system.url}")
            else:
                sap_system_output = utilities.sap_systems_list_into_nametuple(
                    [
                        [
                            system.upper() if system else None,
                            str(mandant).zfill(3) if mandant else None,
                            user.upper() if user else None,
                            None,
                            customer.upper() if customer else None,
                            description.upper() if description else None,
                            None,
                        ]
                    ]
                )

                utilities.print_system_list(
                    sap_system_output,
                    "NO URL FOUND according to search criteria",
                    color=utilities.color_warning,
                )
                sys.exit()
        else:
            if transaction:
                item = "-type=transaction"
                argument.append(item)

                if parameter:
                    # TODO: Доделать запуск транзакции с параметрами: проблема с тем, что когда запускаешь код напрямую,
                    #  например, '-command="/n*FBM1 BKPF-BUKRS=1000;"', то все работает.
                    #  А если формировать код через переменные, например,
                    #  f"-command=\"*{transaction.upper()} {param_data[0][1]}={parameter}\""- то все плохо.

                    # param_data = sap.query_param(str(transaction).upper())

                    # item = f"-command=\"*{transaction.upper()} {param_data[0][1]}={parameter}\""
                    # item = '-command=\"*TM_52 VTGFHA-BUKRS=TRM1; VTGFHA-RFHA=100000000057;\"'
                    item = '-command="/n*FBM1 BKPF-BUKRS=1000;"'
                    argument.append(item)

                    click.echo(item)
                else:
                    item = "-command=" + transaction
                    argument.append(item)

            if external_user:
                message = "Trying to LAUNCH the following system with EXTERNAL USERS"
            else:
                message = "Trying to LAUNCH the following system"
            utilities.print_system_list([selected_system], message, transaction=transaction)

            # Запускаем SAP
            ret = call(argument)

            if ret:
                click.echo(ret)


@sap_cli.command("debug")
@click.argument("system", required=False, type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="User")
@click.option("-c", "--customer", "customer", help="Launch sap system by customer id", type=click.STRING)
@click.option("-d", "--description", "description", help="Launch sap system by customer id", type=click.STRING)
@click.option("-pw", "--password", "password", help="Password")
@click.option("-l", "--language", "language", help="Logon language", default="RU")
@click.option("-f", "--file", "file", help="Create debug file", is_flag=True, type=click.BOOL)
@click.option('-o', "--open_debug_file", "open_file", is_flag=True, default=True,
              help='Do you need to open folder with debug file')
@click.pass_context
def debug(ctx, system, mandant="", user="", customer="", description="", password="", language="RU", file=False,
          open_file=True):
    """
    System debug \n
    You can: \n
    1. Creat debug file - to debug modal dialog box: SAP DEBUG -f \n
    2. Start debuggin of the opened system (the last used windows will be used): SAP DEBUG <SYSTEM> <MANDANT> \n

    Optional arguments: \n
    1. SYSTEM - system id from saplogon \n
    2. MANDANT - mandant or client id of sap system \n
    """

    if file:
        debug_folder = ctx.obj['DEBUG'] if ctx.obj['DEBUG'] else utilities.path()
        debug_file_path = os.path.join(debug_folder, DEBUG_FILE_NAME)

        click.echo(f"\n{debug_file_path} file will be created.")
        click.echo(f"After creation, a folder with {DEBUG_FILE_NAME} file will be opened \n")
        click.echo("Drag the file to the SAP system to start debug mode \n")
        click.pause("Press Enter to continue")

        with open(debug_file_path, "w", encoding='utf-8') as writer:
            writer.write("[FUNCTION]\n")
            writer.write("Command =/H\n")
            writer.write("Title=Debugger\n")
            writer.write("Type=SystemCommand")

        if open_file:
            click.launch(url=debug_file_path, locate=True)

    else:
        query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                                  description=description,
                                  url=False, verbose=False, enum=True)
        # --------------------------
        if query_result != []:
            selected_sap_systems = [
                Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
                for item in query_result]

            argument, selected_system = utilities.prepare_parameters_to_launch_system(selected_sap_systems, '', '',
                                                                                      user, "", ctx.obj[
                                                                                          'CONFIG_DATA'].command_line_path)

            item = "-command=/H"
            argument.append(item)
            item = "-type=SystemCommand"
            argument.append(item)

            utilities.print_system_list([selected_system], "Trying to DEBUG the following system")

            ret = call(argument)


@sap_cli.command("pw")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="User id. Either user from database to narrow system selection "
                                           "if several users exist for one system, or user outside of the database",
              )
@click.option("-c", "--customer", "customer", help="Launch sap system by customer id", type=click.STRING)
@click.option("-d", "--description", "description", help="Launch sap system by customer id", type=click.STRING)
@click.option('-c', "--clear_clipboard", "clear_clipboard", is_flag=True, default=True,
              help='Clear clipboard: True, False. Default value: True')
@click.option('-t', "--time_to_clear", "time_to_clear", default=10, type=click.INT,
              help='Timer in secornds to clear clipboard. Default value: 15')
@click.pass_context
def pw(ctx, system: str, mandant: int, user: str, customer: str, description: str, clear_clipboard: bool = True,
       time_to_clear: int = 10):
    """
    Copy password for the requested system into clipboard.
    Script waits 15 seconds and clears clipboard.

    Required arguments: \n
    1. SYSTEM ID - system id from saplogon \n \n

    Optional argument: \n
    2. MANDANT - mandant or client id of sap system \n
    """

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description,
                              url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        argument, selected_system = utilities.prepare_parameters_to_launch_system(selected_sap_systems, '',
                                                                                  '',
                                                                                  user, "",
                                                                                  ctx.obj[
                                                                                      'CONFIG_DATA'].command_line_path)

        pyperclip.copy(selected_system.password)

        click.echo(
            click.style(
                f"\nPassword is copied into clipboard.\n",
                **utilities.color_message,
            )
        )

        if clear_clipboard:
            click.echo(
                click.style(
                    "If you use Clipboard manager, you should add PY.EXE, CMD.EXE applications to the exclusion list,\n"
                    "in order to keep sensitive information safe.",
                    **utilities.color_sensitive,
                )
            )

            click.echo(
                click.style(
                    f"\nClipboard will be cleared in {time_to_clear} seconds.\n",
                    **utilities.color_message,
                )
            )

            try:
                utilities.countdown(time_to_clear)
            except KeyboardInterrupt:
                print("\nAborted!")
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()

            click.echo(click.style("\nClipboard is cleared. \n", **utilities.color_success))


@sap_cli.command("add")
@click.option("-system", prompt=True, help="System", type=utilities.LETTERS_NUMBERS_3)
@click.option("-mandant", prompt=True, help="Client", type=click.IntRange(1, 999))
@click.option("-user", prompt=True, help="User")
@click.option("-password", help="Password", prompt=True, confirmation_prompt=True, hide_input=True)
@click.option("-customer", prompt=True, help="Customer", type=click.STRING, default="")
@click.option("-description", prompt=True, help="Description", type=click.STRING, default="")
@click.option("-url", prompt=True, help="Url", type=click.STRING, default="")
@click.option("-v", "--verbose", "verbose", help="Show passwords for selected systems", is_flag=True, default=True)
@click.pass_context
def add(ctx, system, mandant, user, password, description, customer, url: str = " ", verbose: bool = True):
    """
    Add sap system with it's parameters to db.

    Just run SAP ADD and enter system parameters
    """

    with _sap_db(ctx.obj['CONFIG_DATA']):
        encrypted_password = ctx.obj['CRYPTO'].encrypto(str.encode(password))
        sap_system = Sap_system(
            str(system).upper(),
            str(mandant).zfill(3),
            str(user).upper(),
            encrypted_password,
            str(customer).upper(),
            str(description),
            str(url),
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

            added_system = [Sap_system(item[0], item[1], item[2], ctx.obj['CRYPTO'].decrypto(item[3]), item[4],
                                       item[5], item[6]) for item in result]
            utilities.print_system_list(added_system, "The following system is ADDED to the database: ",
                                        verbose=verbose)
            if verbose:
                click.echo(f"Information about passwords will be deleted from screen in {TIMER_TO_CLEAR_SCREEN}: \n")
                try:
                    utilities.countdown(TIMER_TO_CLEAR_SCREEN)
                except KeyboardInterrupt:
                    print("Aborted!")
                click.clear()


@sap_cli.command("update")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="User id. Either user from database to narrow system selection "
                                           "if several users exist for one system, or user outside of the database",
              )
@click.option("-c", "--customer", "customer", help="Launch sap system by customer id", type=click.STRING)
@click.option("-d", "--description", "description", help="Launch sap system by customer id", type=click.STRING)
@click.option("-v", "--verbose", "verbose", help="Show passwords for selected systems", is_flag=True, default=False)
@click.pass_context
def update(ctx, system, mandant, user, customer, description, verbose: bool = False):
    """
    Update selected records of database

    Just run SAP UPDATE and enter system parameters to update
    """

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description,
                              url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        argument, selected_system = utilities.prepare_parameters_to_launch_system(selected_sap_systems, "",
                                                                                  "",
                                                                                  user, "",
                                                                                  ctx.obj[
                                                                                      'CONFIG_DATA'].command_line_path)

    password_new = click.prompt("Enter new password", default=selected_system.password)
    customer_new = click.prompt("Enter Customer", default=selected_system.customer)
    description_new = click.prompt("Enter system description", default=selected_system.description)
    url_new = click.prompt("Enter URL", default=selected_system.url)

    sap_encrypted_system = Sap_system(
        str(selected_system.system).upper(),
        str(selected_system.mandant).zfill(3),
        str(selected_system.user).upper(),
        ctx.obj['CRYPTO'].encrypto(str.encode(password_new)),
        str(customer_new),
        str(description_new),
        str(url_new),
    )

    result = sap.update(sap_encrypted_system)

    if result is None:
        result = sap.query_system(sap_encrypted_system)

        updated_system = [
            Sap_system(item[0], item[1], item[2], ctx.obj['CRYPTO'].decrypto(item[3]), item[4], item[5], item[6])
            for
            item in result]

        utilities.print_system_list(updated_system, "The following system is UPDATED", verbose=verbose)

        click.echo(f"Information about passwords will be deleted from screen in {TIMER_TO_CLEAR_SCREEN}: \n")
        try:
            utilities.countdown(TIMER_TO_CLEAR_SCREEN)
        except KeyboardInterrupt:
            print("Aborted!")
        click.clear()
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
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="User id. Either user from database to narrow system selection "
                                           "if several users exist for one system, or user outside of the database",
              )
@click.option("-c", "--customer", "customer", help="Launch sap system by customer id", type=click.STRING)
@click.option("-d", "--description", "description", help="Launch sap system by customer id", type=click.STRING)
@click.pass_context
def delete(ctx, system: str, mandant: str, user: str, customer: str, description: str):
    """ Delete SAP system from database """

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description, url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        argument, selected_system = utilities.prepare_parameters_to_launch_system(selected_sap_systems, "",
                                                                                  "",
                                                                                  user, "",
                                                                                  ctx.obj[
                                                                                      'CONFIG_DATA'].command_line_path)

        message = "Trying to DELETE the following systtem"
        utilities.print_system_list([selected_system], message)

        click.confirm(click.style('Do you really want to delete the system?', **utilities.color_sensitive), abort=True)

        system_to_delete = Sap_system(selected_system.system,
                                      selected_system.mandant,
                                      selected_system.user,
                                      selected_system.password,
                                      selected_system.customer,
                                      selected_system.description,
                                      selected_system.url)

        result = sap.delete(system_to_delete)

        result = sap.query_system(system_to_delete)

        if result == []:

            utilities.print_system_list([system_to_delete], "The following system is DELETED from database")
        else:
            sap_system_output = utilities.sap_systems_list_into_nametuple(
                list(list(str(system).upper(), str(mandant).zfill(3) if mandant else "",
                          str(user).upper() if user else "", "", "", "", ""))

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
@click.argument("system", required=False, type=click.STRING, default=None)
@click.argument("mandant", required=False, type=click.IntRange(1, 999), default=None)
@click.option("-u", "--user", "user", help="Show systems by user", type=click.STRING, default=None)
@click.option("-c", "--customer", "customer", help="Show systems by customer", type=click.STRING, default=None)
@click.option("-d", "--description", "description", help="Show systems by description", type=click.STRING, default=None)
@click.option("-u", "--url", "url", help="Display url", is_flag=True, type=click.BOOL, default=False)
@click.option("-v", "--verbose", "verbose", help="Show passwords for selected systems", is_flag=True, default=False)
@click.option("-e", "--enum", "enum", help="Enumerate systems", is_flag=True, default=False)
@click.pass_context
def list_systems(ctx, system: str, mandant: int, user: str, customer: str, description: str, url: bool,
                 verbose: bool, enum: bool) -> list:
    """
    Print information about SAP systems

    Optional arguments: \n
    1. System: System Id \n
    2. Mandant: Mandant num \n

    If no arguments - print information about all systems
    """

    with _sap_db(ctx.obj['CONFIG_DATA']):
        sap_system_sql = Sap_system(str(system).upper() if system else None, str(mandant) if mandant else None,
                                    user if user else None, None, customer if customer else None,
                                    description if description else None, None)
        result = sap.query_system(sap_system_sql)

        if not result:
            no_system_found = [Sap_system(str(system).upper() if system else "",
                                          str(mandant).zfill(3) if mandant else "",
                                          user.upper() if user else "",
                                          "",
                                          str(customer).upper() if customer else "",
                                          description.upper() if description else "",
                                          "")]
            utilities.print_system_list(
                no_system_found,
                "NOTHING FOUND according to search criteria",
                color=utilities.color_warning,
            )
            return list()
        else:
            sap_system = [
                Sap_system(item[0], item[1], item[2], ctx.obj['CRYPTO'].decrypto(item[3]), item[4], item[5], item[6])
                for item in result]

            utilities.print_system_list(sap_system, "Available systems", verbose=verbose, url=url, enum=enum)
            if verbose:
                click.echo(f"Information about passwords will be deleted from screen in {TIMER_TO_CLEAR_SCREEN}: \n")
                try:
                    utilities.countdown(TIMER_TO_CLEAR_SCREEN)
                except KeyboardInterrupt:
                    print("Aborted!")
                click.clear()

            return sap_system


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


@sap_cli.command("ver", help="Current version of SAP shortcut")
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

    print("\nThe following files are created:")
    print(f"1. [yellow]{PUBLIC_KEY_NAME}[/yellow] - used to encrypt passwords in database")
    print(
        f"      can be stored in any place. If you move it from default location then don't forget to put new place in {CONFIG_NAME} -> '[KEYS]' -> 'public_key_path'")
    print(f"2. [yellow]{PRIVATE_KEY_NAME}[/yellow] - used to decrypt passwords")
    print(
        f"      must be stored in [bright_red]secure place[/bright_red]. For example, in Bestcrypt container. Don't forget to put new place in {CONFIG_NAME} -> '[KEYS]' -> 'private_key_path'")
    print(f"3. [yellow]{DATABASE_NAME}[/yellow] - used to store all information about SAP systems")
    print(
        f"      must be stored in [bright_red]secure place[/bright_red]. For example, in Bestcrypt container. Don't forget to put new place in {CONFIG_NAME} -> '[DATABASE]' -> 'db_path'")
    print(f"4. [yellow]{CONFIG_NAME}[/yellow] - used to store information about all previous files locations")
    print(
        f"      must be stored only in [bright_red] {ctx.obj['CONFIG_METHODS'].config_path} [/bright_red] folder.")
    print("\n")
    print(f"Extra work:")
    print(
        f"5. Find 'SAPSHCUT.EXE' file and put it's location in {CONFIG_NAME} -> '[APPLICATION]' -> 'command_line_path'")
    print(f"5. Find 'SAPLOGON.EXE' file and put it's location in {CONFIG_NAME} -> '[APPLICATION]' -> 'saplogon_path'")

    print("\n")
    print("To start work with SAP commands after preparatory work:")
    print("type 'SAP ADD' to add sap system into database")
    print("type 'SAP RUN <system id> <mandant num>' to launch sap system")
    print("type 'SAP --HELP' to learn more about programm")

    click.pause('\nPress enter to open files folder and start working. Good luck.')

    click.launch(ctx.obj['CONFIG_METHODS'].config_file_path, locate=True)


@sap_cli.command("backup")
@click.option("-password", help="Password for backup", prompt=True, confirmation_prompt=True, hide_input=True,
              type=utilities.PASS_REQUIREMENT)
@click.option('-o', "--open_debug_file", "open_file", is_flag=True, default=True,
              help='Do you need to open folder with backup file')
@click.pass_context
def backup(ctx, password, open_file=True):
    """
    Create back up for the following files: \n
    1. saplogon systems (SAPUILandscape.xml) \n
    2. database \n
    3. cypher files \n
    4. sap_config.ini \n
    """

    #  Paths to SAPUILandscape.xml: https://launchpad.support.sap.com/#/notes/2075150

    pwd = str.encode(password)

    config_ini_path = os.path.join(utilities.path(), CONFIG_NAME)

    # saplogon_ini_path = utilities.get_reg('CoreLandscapeFileOnServer')
    saplogon_ini_path = os.path.join(os.path.expandvars(r'%APPDATA%\SAP\Common'), 'SAPUILandscape.xml')

    back_file_name = f'backup_{datetime.now().strftime("%Y.%m.%d-%I.%M.%S")}.zip'
    back_path = os.path.join(utilities.path(), back_file_name)
    with pyzipper.AESZipFile(back_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(pwd)
        zf.write(ctx.obj['CONFIG_DATA'].db_path, os.path.basename(ctx.obj['CONFIG_DATA'].db_path))
        zf.write(ctx.obj['CONFIG_DATA'].public_key_path, os.path.basename(ctx.obj['CONFIG_DATA'].public_key_path))
        zf.write(ctx.obj['CONFIG_DATA'].private_key_path, os.path.basename(ctx.obj['CONFIG_DATA'].private_key_path))
        zf.write(config_ini_path, os.path.basename(config_ini_path))
        zf.write(saplogon_ini_path, os.path.basename(saplogon_ini_path))

        zf.comment = b""" 
            \n 1. Place 'SAPUILandscape.xml' to '%APPDATA%\SAP\Common' folder 
            \n 2. Place 'sap_config.ini' to 'c:\Users\<USERNAME>\AppData\Local\SAP' folder
            \n 3. Other files - according to sap_config.ini paths
            \n Or you can place whener you want, just enter new paths to sap_config.ini
            \n !!! And remember that files 'database.db' and 'private_key.txt' must be stored in secure place"""

    if os.path.exists(back_path):
        click.echo(click.style('Backup succesfully created', **utilities.color_success))
        if open_file:
            click.launch(url=back_path, locate=True)
    else:
        click.echo('Backup creation failed')


@contextmanager
def _sap_db(cfg):
    sap.start_sap_db(cfg.db_path, cfg.db_type)
    yield
    sap.stop_sap_db()


if __name__ == "__main__":
    sys.excepthook = utilities.show_exception_and_exit
    # sys.tracebacklimit = 0  # Stop printing traceback. Only messages for exceptions.
    sap_cli(obj={})
