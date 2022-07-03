#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import ctypes
import getpass
import os
from contextlib import contextmanager
from datetime import datetime
from subprocess import Popen
import click_log
import logging
import click
import time
import pyautogui
import pyperclip
import pyzipper
import re
import rich_click as click
from rich import print

import sap.config
from sap import utilities
from sap.api import Sap_system, Obj_structure
from sap.config import create_config, open_config, open_folder
from sap.crypto import Crypto
from sap.database import SapDB
from sap.api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, CONFIG_NAME, DATABASE_NAME, DEBUG_FILE_NAME, \
    TIMER_TO_CLEAR_SCREEN
from sap.exceptions import DatabaseDoesNotExists, ConfigDoesNotExists, WrongPath, ConfigExists, \
    EncryptionKeysAlreadyExist, DatabaseExists

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'],
                        show_default=True, token_normalize_func=lambda x: x.lower())

log_level = ['--log_level', '-l']


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option('-path', '--config_path', 'config_path', help="Path to external sap_config.ini folder", type=click.Path())
@click.version_option(version=sap.__version__)
@click_log.simple_verbosity_option(logger, *log_level, default='ERROR')
def sap_cli(ctx, config_path: str, verbosity=''):
    """
    \b
    Command line tool for launching SAP systems from SAPLogon\n
    \b
    Run 'sap start' to start working
    """

    ctx.obj = Obj_structure()

    # ========= CONFIG =========
    ctx.obj.config = sap.config.Config(config_path)

    if ctx.invoked_subcommand != "start" and ctx.invoked_subcommand != "config":
        try:
            _config = ctx.obj.config.read()
        except ConfigDoesNotExists as err:
            click.echo(click.style(f"{err}", **utilities.color_warning))
            raise click.Abort

        ctx.obj.config.db_path = _config.db_path
        ctx.obj.config.db_type = _config.db_type
        ctx.obj.config.private_key_path = _config.private_key_path
        ctx.obj.config.public_key_path = _config.public_key_path
        ctx.obj.config.command_line_path = _config.command_line_path
        ctx.obj.config.saplogon_path = _config.saplogon_path

    # ========= CRYPTO =========
    ctx.obj.crypto = Crypto(ctx.obj.config.public_key_path, ctx.obj.config.private_key_path)

    # ========= DATABASE =========

    ctx.obj.database = SapDB(db_path=ctx.obj.config.db_path if ctx.obj.config.db_path else '')


@sap_cli.command("logon")
@click.pass_context
def logon(ctx):
    """Launch SAPLogon application"""

    try:
        utilities.launch_saplogon_with_params(ctx.obj.config.saplogon_path)
    except WrongPath as err:
        utilities.print_message(f"{err}", utilities.message_type_error)
        raise click.Abort


@sap_cli.command("run")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user", type=click.STRING)
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option("-eu", "--external_user", "external_user", default=False, is_flag=True,
              help="Flag. Launch sap system with external user (outside database)")
@click.option("-l", "--language", "language", help="Logon language", type=click.STRING)
@click.option("-g", "--guiparm", "guiparm", help="Parameter of sapgui.exe", type=click.STRING)
@click.option("-sname", "--snc_name", "snc_name",
              help="SNC name of the SAP system; required for the logon via Secure Network Communication (SNC)",
              type=click.STRING)
@click.option("-sqop", "--snc_qop", "snc_qop", help="Activation of the logon via Secure Network Communication (SNC)",
              type=click.STRING)
@click.option("-t", "--transaction", "transaction", help="Run transaction ", type=click.STRING)
@click.option("-s", "--system_command", "system_command",
              help="Run system_command: /n, /o, /i, /nend, /nex, /*<transaction_code>, /n<transaction_code>, /o<transaction_code>, /h")
@click.option("-r", "--report", "report", help="Run report (report name for SE38 transaction)", type=click.STRING)
@click.option("-p", "--parameter", "parameter", help="Transaction's parameters")
@click.option("-w", "--web", "web", help="Flag. Launch system's web site", default=False, is_flag=True)
@click.option("-n", "--new", "reuse", help="Flag. Defines whether a new connection to an SAP is reused",
              default=True, is_flag=True)
@click.pass_context
def run(ctx, system: str, mandant: int, user: str, customer: str, description: str, external_user: bool,
        language: str, guiparm: str, snc_name: str, snc_qop: str, transaction: str, system_command: str, report: str,
        parameter: str, web: bool, reuse: bool):
    """
    \b
    Launch SAP system \n
    \b
    Optional arguments:
    1. SYSTEM: Request a SAP system by systedm id
    2. MANDANT: Request a SAP system by mandant/client
    """
    password = ""

    if snc_name is not None and snc_qop is None or snc_name is None and snc_qop is not None:
        utilities.print_message(f"\nBoth parameters must be used: -sname/--snc_name and -sqop/--snc_qop",
                                utilities.message_type_warning)
        raise click.Abort

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
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            for item in query_result]

        if language is None:
            language = ctx.obj.config.language

        selected_system = utilities.choose_system(selected_sap_systems)
        try:
            argument = utilities.prepare_parameters_to_launch_system(selected_system, password,
                                                                     language,
                                                                     guiparm, snc_name, snc_qop,
                                                                     user, "",
                                                                     ctx.obj.config.command_line_path)
        except WrongPath as err:
            utilities.print_message(f"{err}", message_type=utilities.message_type_error)
            raise click.Abort

        if web:
            if selected_system.url != " ":
                # TODO: доделать передачу пароля для авторизации по аналогии с KeePass
                #   https://keepass.info/help/base/autotype.html
                #   https://github.com/allo-/passautotype - РЕАЛИЗАЦИЯ
                #   Сделать настройку для каждого сайта - т.е. отдельная таблица по параметрам сайтов

                utilities.print_message(
                    f"\nLaunching web site: {selected_system.description} of {selected_system.customer}",
                    message_type=utilities.message_type_message)
                click.launch(url=f"{selected_system.url}")

                time.sleep(4)

                key_strokes = re.findall(r'{(.+?)}', selected_system.autotype)
                logger.info(f"Autotype from database: {selected_system.autotype}")

                for item in key_strokes:
                    if item == 'USER':
                        pyautogui.write(str(selected_system.user))
                    elif item == 'PASS':
                        pyautogui.write(str(selected_system.password))
                    else:
                        pyautogui.press(item)

            else:
                no_system_found = Sap_system(system.upper() if system else None,
                                             str(mandant).zfill(3) if mandant else None,
                                             user.upper() if user else None,
                                             None,
                                             customer.upper() if customer else None,
                                             description.upper() if description else None,
                                             None,
                                             None)

                utilities.print_system_list(no_system_found,
                                            title="NO URL FOUND according to search criteria",
                                            color=utilities.color_warning)
                raise click.Abort
        else:
            if transaction:
                command = transaction
                command_type = 'transaction'

                argument = argument + " -type=transaction"

                if parameter:
                    param_data = sap.query_param(str(transaction).upper())

                    if param_data:
                        argument = argument + f' -command="{transaction.upper()} {param_data[0][1]}={parameter};"'
                    else:
                        utilities.print_message(f"\nThere is no parameter info for {transaction.upper()} transaction",
                                                message_type=utilities.message_type_warning)

                        argument = argument + f' -command="{transaction.upper()}"'
                else:
                    argument = argument + " -command=" + transaction
            elif system_command:
                command = system_command
                command_type = 'system command'

                argument = argument + " -type=SystemCommand"
                argument = argument + " -command=" + system_command

            elif report:
                command = report
                command_type = 'report'

                argument = argument + " -type=report"
                argument = argument + " -command=" + report
            else:
                command = None
                command_type = None

            if external_user:
                message = "Trying to LAUNCH the following system with EXTERNAL USERS"
            else:
                message = "Trying to LAUNCH the following system "

            if reuse:
                argument = argument + f' -reuse=1'
            else:
                argument = argument + f' -reuse=0'

            utilities.print_system_list(selected_system, title=message,
                                        command=command, command_type=command_type)

            logger.info(f"{argument}")

            # Запускаем SAP
            pop = Popen(argument)
            pop.wait()

            if pop.returncode:
                click.echo(pop.returncode, pop.communicate()[0])


@sap_cli.command("debug", short_help="System debug: either create debug file or start system debuggin")
@click.argument("system", required=False, type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option("-l", "--language", "language", help="Logon language")
@click.option("-g", "--guiparm", "guiparm", help="Parameter of sapgui.exe", type=click.STRING)
@click.option("-sname", "--snc_name", "snc_name",
              help="SNC name of the SAP system; required for the logon via Secure Network Communication (SNC)",
              type=click.STRING)
@click.option("-sqop", "--snc_qop", "snc_qop", help="Activation of the logon via Secure Network Communication (SNC)",
              type=click.STRING)
@click.option("-f", "--file", "file", help="Flag. Create debug file", is_flag=True, type=click.BOOL)
@click.option('-o', "--open_debug_file", "open_file", help="Flag. Open file with debug file", is_flag=True,
              default=True)
@click.pass_context
def debug(ctx, system: str, mandant: str, user: str, customer: str, description: str, language: str, guiparm: str,
          snc_name: str, snc_qop: str, file: bool, open_file: bool):
    """
    \b
    System debug
    You can:
    1. Creat debug file - to debug modal dialog box: run 'sap debug -f'
    2. Start debuggin of the opened system (the last used windows will be used): run 'sap debug <system> <mandant>'
    \b
    Optional arguments:
    1. SYSTEM: Request a SAP system by system
    2. MANDANT: Request a SAP system by mandant/clien
    """

    if file:
        debug_folder = ctx.obj.config.config_path if ctx.obj.config.config_path else utilities.path()
        debug_file_path = os.path.join(debug_folder, DEBUG_FILE_NAME)

        debug_markdown = f"""
        # DEBUG
        
        {debug_file_path} file will be created.
        After creation, a folder with {DEBUG_FILE_NAME} file will be opened
        Drag the file to the SAP system to start debug mode
        """

        utilities.print_markdown(debug_markdown)

        # click.echo(f"\n{debug_file_path} file will be created.")
        # click.echo(f"After creation, a folder with {DEBUG_FILE_NAME} file will be opened \n")
        # click.echo("Drag the file to the SAP system to start debug mode \n")
        # click.pause("Press Enter to continue")

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

            if language is None:
                language = ctx.obj.config.language

            # As soon as dubugger stops working - revert all the changes to "prepare_parameters_to_launch_system"
            #  as it influence whether to open new windows, or to debug the latest opened. All arguments
            #  values must be entered
            selected_system = utilities.choose_system(selected_sap_systems)
            try:
                argument = utilities.prepare_parameters_to_launch_system(selected_system, None,
                                                                         language,
                                                                         guiparm, snc_name, snc_qop,
                                                                         None,
                                                                         user, "",
                                                                         ctx.obj.config.command_line_path)
            except WrongPath as err:
                click.echo(f"{err}")
                raise click.Abort

            argument = argument + " -command=/H" + " -type=SystemCommand"

            utilities.print_system_list(selected_system, title="Trying to DEBUG the following system")

            logger.info(f"{argument}")

            pop = Popen(argument)
            pop.wait()

            if pop.returncode:
                click.echo(pop.returncode, pop.communicate()[0])


@sap_cli.command("stat")
@click.argument("system", required=False, type=utilities.LETTERS_NUMBERS_3)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option("-l", "--language", "language", help="Logon language")
@click.pass_context
def stat(ctx, system: str, mandant: str, user: str, customer: str, description: str, language: str):
    """
    \b
    Displays 'System: status' window \n
    \b
    Optional arguments:
    1. SYSTEM: Request a SAP system by system id
    2. MANDANT: Request a SAP system by mandant/client
    """

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description,
                              url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        if language is None:
            language = ctx.obj.config.language

        selected_system = utilities.choose_system(selected_sap_systems)
        try:
            argument = utilities.prepare_parameters_to_launch_system(selected_system, None,
                                                                     language,
                                                                     None, None, None,
                                                                     user, "",
                                                                     ctx.obj.config.command_line_path)
        except WrongPath as err:
            click.echo(f"{err}")
            raise click.Abort

        argument = argument + " -command=?STAT" + " -type=SystemCommand"

        utilities.print_system_list(selected_system, title="Opening STATUS of the following system")

        logger.info(f"{argument}")

        pop = Popen(argument)
        pop.wait()

        if pop.returncode:
            click.echo(pop.returncode, pop.communicate()[0])


@sap_cli.command("pw")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option('-c', "--clear_clipboard", "clear_clipboard", is_flag=True, default=True,
              help='Flag. Clear clipboard.')
@click.option('-t', "--time_to_clear", "time_to_clear", default=10, type=click.INT,
              help='Timer in seconds to clear clipboard')
@click.pass_context
def pw(ctx, system: str, mandant: int, user: str, customer: str, description: str, clear_clipboard: bool,
       time_to_clear: int):
    """
    \b
    Copy password for the requested system into clipboard.
    Script waits 10 seconds and clears clipboard.\n
    \b
    Optional argument:
    1. SYSTEM: Request a SAP system by system id
    2. MANDANT: Request a SAP system by mandant/client
    """

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description,
                              url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        selected_system = utilities.choose_system(selected_sap_systems)

        pyperclip.copy(selected_system.password)

        utilities.print_message("Password is copied into clipboard.", message_type=utilities.message_type_message)

        if clear_clipboard:
            utilities.print_message(
                "If you use Clipboard managers, you should add PY.EXE, CMD.EXE applications to the exclusion list,\nin order to keep sensitive information safe from copying to clipboard manager.",
                message_type=utilities.message_type_sensitive)

            utilities.print_message(f"Clipboard will be cleared in {time_to_clear} seconds.",
                                    message_type=utilities.message_type_message)

            try:
                utilities.countdown(time_to_clear)
            except KeyboardInterrupt:
                click.echo("\n")
                utilities.print_message(f"Aborted",
                                        message_type=utilities.message_type_error)
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()

            click.echo("\n")
            utilities.print_message(f"Clipboard is cleared.", message_type=utilities.message_type_message)


@sap_cli.command("add")
@click.option("-system", prompt=True, help="System Id", type=utilities.LETTERS_NUMBERS_3)
@click.option("-mandant", prompt=True, help="Mandant/Client number", type=click.IntRange(1, 999))
@click.option("-user", prompt=True, help="User")
@click.option("-password", help="Password", prompt=True, confirmation_prompt=True, hide_input=True)
@click.option("-customer", prompt=True, help="Customer name", type=click.STRING, default="")
@click.option("-description", prompt=True, help="SAP system description", type=click.STRING, default="")
@click.option("-url", prompt=True, help="SAP system Url", type=click.STRING, default="")
@click.option("-v", "--verbose", "verbose", help="Show passwords for selected systems", is_flag=True, default=True)
@click.pass_context
def add(ctx, system: str, mandant: str, user: str, password: str, description: str, customer: str, url: str,
        verbose: bool):
    """
    Add sap system with it's parameters to db. Just run 'sap add' and follow instructions.
    """

    with _sap_db(ctx.obj.config):
        encrypted_password = ctx.obj.crypto.encrypto(str.encode(password))
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
            sap_system = Sap_system(str(system).upper() if system else None, str(mandant) if mandant else None,
                                    user.upper() if user else None)
            result = sap.query_system(sap_system)

            added_system = [Sap_system(item[0], item[1], item[2], ctx.obj.crypto.decrypto(item[3]), item[4],
                                       item[5], item[6]) for item in result]
            utilities.print_system_list(*added_system, title="The following system is ADDED to the database: ",
                                        verbose=verbose)
            if verbose:
                click.echo(f"Information about passwords will be deleted from screen in {TIMER_TO_CLEAR_SCREEN}: \n")
                try:
                    utilities.countdown(TIMER_TO_CLEAR_SCREEN)
                except KeyboardInterrupt:
                    click.echo("Aborted!")
                click.clear()


@sap_cli.command("update", short_help="Update record from database")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option("-v", "--verbose", "verbose", help="Show passwords for selected systems", is_flag=True, default=True)
@click.pass_context
def update(ctx, system: str, mandant: str, user: str, customer: str, description: str, verbose: bool):
    """
    \b
    Update password, customer, system description or url of the requested record from database\n
    \b
    Optional arguments:
    1. SYSTEM: Request a SAP system by system id
    2. MANDANT: Request a SAP system by mandant/client
    """

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description,
                              url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        selected_system = utilities.choose_system(selected_sap_systems)

        password_new = click.prompt("\nEnter new password", default=selected_system.password)
        customer_new = click.prompt("Enter Customer", default=selected_system.customer)
        description_new = click.prompt("Enter system description", default=selected_system.description)
        url_new = click.prompt("Enter URL", default=selected_system.url)

        sap_encrypted_system = Sap_system(
            str(selected_system.system).upper(),
            str(selected_system.mandant).zfill(3),
            str(selected_system.user).upper(),
            ctx.obj.crypto.encrypto(str.encode(password_new)),
            str(customer_new),
            str(description_new),
            str(url_new),
        )

        result = sap.update(sap_encrypted_system)

        if result is None:
            result = sap.query_system(sap_encrypted_system)

            updated_system = [
                Sap_system(item[0], item[1], item[2], ctx.obj.crypto.decrypto(item[3]), item[4], item[5], item[6])
                for item in result]

            utilities.print_system_list(*updated_system, title="The following system is UPDATED", verbose=verbose)

            click.echo(f"Information about passwords will be deleted from screen in {TIMER_TO_CLEAR_SCREEN}: \n")
            try:
                utilities.countdown(TIMER_TO_CLEAR_SCREEN)
            except KeyboardInterrupt:
                click.echo("Aborted!")
            click.clear()
        else:
            no_system_found = Sap_system(system.upper() if system else None,
                                         str(mandant).zfill(3) if mandant else None,
                                         user.upper() if user else None,
                                         None,
                                         customer.upper() if customer else None,
                                         description.upper() if description else None,
                                         None)

            utilities.print_system_list(no_system_found, title="FAILED TO UPDATE the following system",
                                        color=utilities.color_warning)


@sap_cli.command("delete")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by usdf")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option("-confirm", "--confirm", "confirm", help="Confirm delete command", default=None,
              type=click.BOOL)
@click.pass_context
def delete(ctx, system: str, mandant: str, user: str, customer: str, description: str, confirm: bool):
    """
    \b
    Delete requested record about SAP system from database\n
    \b
    Optional arguments:
    1. SYSTEM: Request a SAP system by system id
    2. MANDANT: Request a SAP system by mandant/client
    """

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description, url=False, verbose=False, enum=True)
    # --------------------------
    if query_result != []:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            for item in query_result]

        selected_system = utilities.choose_system(selected_sap_systems)

        message = "Trying to DELETE the following systtem"
        utilities.print_system_list(selected_system, title=message)

        click.confirm(click.style('\nDo you really want to delete the system?', **utilities.color_sensitive),
                      abort=True, default=confirm)

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

            utilities.print_system_list(system_to_delete, title="The following system is DELETED from database")
        else:
            no_system_found = Sap_system(system.upper() if system else None,
                                         str(mandant).zfill(3) if mandant else None,
                                         user.upper() if user else None,
                                         None,
                                         customer.upper() if customer else None,
                                         description.upper() if description else None,
                                         None)

            utilities.print_system_list(no_system_found, title="FAILED TO UPDATE the following system",
                                        color=utilities.color_warning)


@sap_cli.command("config")
@click.option('-create', is_flag=True, callback=create_config, expose_value=False, is_eager=True,
              help='Create config file')
@click.option('-open', is_flag=True, callback=open_config, expose_value=False, is_eager=True,
              help='Open config file')
@click.option('-folder', is_flag=True, callback=open_folder, expose_value=False, is_eager=True,
              help='Open config folder')
@click.pass_context
def config(ctx):
    """ Config file creation or editing """

    config_markdown = """
    Enter one of subcommands:

    \t -create       Create config file
    \t -open         Open config file
    \t -folder       Open config folder
    """

    utilities.print_markdown(config_markdown)


@sap_cli.command("list", short_help="Print information about SAP systems")
@click.argument("system", required=False, type=click.STRING, default=None)
@click.argument("mandant", required=False, type=click.IntRange(0, 999), default=None)
@click.option("-u", "--user", "user", help="Request a SAP system by user", type=click.STRING, default=None)
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING, default=None)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING,
              default=None)
@click.option("-url", "--show_url", "url", help="Flag. Display url of the requested SAP sytem", is_flag=True,
              type=click.BOOL,
              default=False)
@click.option("-v", "--verbose", "verbose", help="Flag. Display passwords of the requested SAP sytem", is_flag=True,
              type=click.BOOL, default=False)
@click.option("-e", "--enum", "enum", help="Flag. Enumerate systems", is_flag=True, type=click.BOOL, default=False)
@click.pass_context
def list_systems(ctx, system: str, mandant: int, user: str, customer: str, description: str, url: bool,
                 verbose: bool, enum: bool) -> list:
    """
    \b
    Print information about SAP systems \b
    \b
    Optional arguments:
    1. System: Request a SAP system by system id
    2. Mandant: Request a SAP system by mandant/client\n
    \b
    If no arguments - print information about all SAP systems from database
    """

    result = ""

    with _sap_db(ctx.obj.config):
        sap_system_sql = Sap_system(str(system).upper() if system else None,
                                    str(mandant) if mandant else None,
                                    user if user else None, None,
                                    customer if customer else None,
                                    description if description else None,
                                    None,
                                    None)
        result = sap.query_system(sap_system_sql)

        if not result:
            no_system_found = Sap_system(str(system).upper() if system else "",
                                         str(mandant).zfill(3) if mandant else "",
                                         user.upper() if user else "",
                                         "",
                                         str(customer).upper() if customer else "",
                                         description.upper() if description else "",
                                         "",
                                         "")
            utilities.print_system_list(no_system_found, title="NOTHING FOUND according to search criteria",
                                        color=utilities.color_warning, )
            return list()
        else:
            sap_system = [
                Sap_system(item[0], item[1], item[2], ctx.obj.crypto.decrypto(item[3]), item[4], item[5], item[6],
                           item[7])
                for item in result]

            utilities.print_system_list(*sap_system, title="Available systems", verbose=verbose, url=url,
                                        enum=enum)
            if verbose:
                utilities.print_message(
                    f"Information about passwords will be deleted from screen in {TIMER_TO_CLEAR_SCREEN}",
                    utilities.message_type_message)
                try:
                    utilities.countdown(TIMER_TO_CLEAR_SCREEN)
                except KeyboardInterrupt:
                    utilities.print_message("Aborted!", utilities.message_type_error)
                click.clear()

            return sap_system


@sap_cli.command("db")
@click.pass_context
def database(ctx):
    """ Database creation. This command is used for technical purpose. Better run 'sap start' command. """
    try:
        ctx.obj.database.create()
    except DatabaseExists as err:
        utilities.print_message(f"{err}", utilities.message_type_warning)
        raise click.Abort


@sap_cli.command("keys")
@click.pass_context
def keys(ctx):
    """ Encryption keys creation. This command is used for technical purpose. Better run 'sap start' command. """
    try:
        ctx.obj.crypto.generate_keys()
    except EncryptionKeysAlreadyExist as err:
        utilities.print_message(f"{err}", utilities.message_type_warning)
        raise click.Abort


@sap_cli.command("about", help="Display 'About SAP logon' window")
@click.pass_context
def about(ctx):
    """ Displays a dialog box with version information about SAP shortcut """
    parameter = "-version"
    logger.info(f"{[ctx.obj.config.command_line_path, parameter]}")
    try:
        utilities.launch_command_line_with_params(ctx.obj.config.command_line_path, parameter)
    except WrongPath as err:
        utilities.print_message(f"{err}", utilities.message_type_error)


@sap_cli.command("shortcut", help="Display 'SAP GUI Shortcut' window")
@click.pass_context
def shortcut(ctx):
    """ Displays a brief help text about the parameterization of SAP shortcut """
    parameter = "-help"
    logger.info(f"{[ctx.obj.config.command_line_path, parameter]}")
    try:
        utilities.launch_command_line_with_params(ctx.obj.config.command_line_path, parameter)
    except WrongPath as err:
        utilities.print_message(f"{err}", utilities.message_type_error)


@sap_cli.command("start", short_help="Starting point for working wiht SAP command line tool")
@click.pass_context
def start(ctx):
    """
    \b
    Starting point for working wiht SAP command line tool
    1. Database creation.
    2. ini file with config parameters createion.
    3. Usefull messages
    """

    click.clear()

    try:
        ctx.obj.config.create()
    except ConfigExists as err:
        utilities.print_message(f"{err}", message_type=utilities.message_type_warning)
        raise click.Abort

    try:
        ctx.obj.crypto.generate_keys()
    except EncryptionKeysAlreadyExist as err:
        utilities.print_message(f"{err}", message_type=utilities.message_type_warning)
        raise click.Abort

    try:
        ctx.obj.database.create()
    except DatabaseExists as err:
        utilities.print_message(f"{err}", message_type=utilities.message_type_warning)
        raise click.Abort

    # TODO: переделать на rich

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
        f"      must be stored only in [bright_red] {ctx.obj.config.config_path} [/bright_red] folder.")
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

    click.launch(ctx.obj.config.config_file_path, locate=True)


@sap_cli.command("backup", short_help="Create backup")
@click.option("-password", help="Password for backup", prompt=True, confirmation_prompt=True, hide_input=True,
              type=utilities.PASS_REQUIREMENT)
@click.option('-o', "--open_debug_file", "open_file", is_flag=True, default=True,
              help='Do you need to open folder with backup file')
@click.pass_context
def backup(ctx, password, open_file=True):
    """
    \b
    Create backup for the following files:
    1. list of saplogon systems (SAPUILandscape.xml)
    2. database
    3. encryption keys (private and public)
    4. sap_config.ini
    """

    #  Paths to SAPUILandscape.xml: https://launchpad.support.sap.com/#/notes/2075150

    pwd = str.encode(password)

    config_ini_path = ctx.obj.config.config_file_path
    saplogon_ini_path = os.path.join(os.path.expandvars(r'%APPDATA%\SAP\Common'), 'SAPUILandscape.xml')

    back_file_name = f'backup_{datetime.now().strftime("%Y.%m.%d-%I.%M.%S")}.zip'
    back_path = os.path.join(utilities.path(), back_file_name)
    with pyzipper.AESZipFile(back_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(pwd)
        zf.write(ctx.obj.config.db_path, os.path.basename(ctx.obj.config.db_path))
        zf.write(ctx.obj.config.public_key_path, os.path.basename(ctx.obj.config.public_key_path))
        zf.write(ctx.obj.config.private_key_path, os.path.basename(ctx.obj.config.private_key_path))
        zf.write(config_ini_path, os.path.basename(config_ini_path))
        zf.write(saplogon_ini_path, os.path.basename(saplogon_ini_path))

        comment = r""" 
            1. Place 'SAPUILandscape.xml' to '%APPDATA%\SAP\Common' folder 
            2. Place 'sap_config.ini' to 'c:\Users\<USERNAME>\AppData\Local\SAP' folder
            3. Other files - according to sap_config.ini paths
            Or you can place whener you want, just enter new paths to sap_config.ini
            !!! And remember that files 'database.db' and 'private_key.txt' must be stored in secure place"""

        zf.comment = comment.encode()

    if os.path.exists(back_path):
        utilities.print_message('Backup succesfully created', message_type=utilities.message_type_message)
        if open_file:
            click.launch(url=back_path, locate=True)
    else:
        utilities.print_message('Backup creation failed', message_type=utilities.message_type_error)
        click.echo()


@contextmanager
def _sap_db(cfg):
    sap.start_sap_db(cfg.db_path, cfg.db_type)
    yield
    sap.stop_sap_db()


if __name__ == "__main__":
    sap_cli()
