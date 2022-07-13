#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Command line interface for sap-from-command-line tool """

import ctypes
import os
import sys
from contextlib import contextmanager
import logging
import time
from pathlib import Path
import click_log
import click
import pyperclip

import rich_click as click  # rich help output. Do not delete it as it works in background
from rich.console import Console
from rich.markdown import Markdown

import sap.config
from sap import utilities
from sap.api import Sap_system, Obj_structure, Parameter
from sap.config import create_config, open_config, open_folder
from sap.crypto import Crypto
from sap.database import SapDB
from sap.api import DEBUG_FILE_NAME, SAPLOGON_INI
from sap.exceptions import ConfigDoesNotExists, WrongPath, ConfigExists, EncryptionKeysAlreadyExist, DatabaseExists
from sap.backup import Backup

if (sys.version_info[0] < 3) or (sys.version_info[0] == 3 and sys.version_info[1] < 9):
    utilities.print_message("Python must be using Python 3.9 or above", utilities.message_type_error)
    sys.exit()

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'],
                        show_default=True, token_normalize_func=lambda x: x.lower())

log_level = ['--log_level', '-l']


# TODO: Если я обновил настройку конфигурационного файл, то как мне ее передать пользователю ?
#  https://stackoverflow.com/questions/52392102/how-to-update-an-existing-section-in-python-config-file-python-3-6-6
#  По такому же принципу работать с базой данных - посмотреть в сторону alembic
#  https://alembic.sqlalchemy.org/en/latest/


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option('-path', '--config_path', 'config_path', help="Path to external sap_config.ini folder", type=click.Path())
@click.version_option(version=sap.__version__)
@click_log.simple_verbosity_option(logger, *log_level, default='ERROR')
def sap_cli(ctx, config_path: str):
    """
    \b
    Command line tool for launching SAP systems from SAPLogon\n
    \b
    Run 'sap start' to start working
    """

    ctx.obj = Obj_structure()

    # ========= CONFIG =========
    ctx.obj.config = sap.config.Config(config_path)

    if ctx.invoked_subcommand not in ("start", "config"):
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
        ctx.obj.config.wait_site_to_load = _config.wait_site_to_load
        ctx.obj.config.sequence = _config.sequence

    # ========= CRYPTO =========
    ctx.obj.crypto = Crypto(ctx.obj.config.public_key_path, ctx.obj.config.private_key_path)

    # ========= DATABASE =========

    ctx.obj.database = SapDB(db_path=ctx.obj.config.db_path if ctx.obj.config.db_path else '')


@sap_cli.command("logon")
@click.option("-s", "--saplogon", "saplogon", help="Path to saplogon.exe file")
@click.pass_context
def logon(ctx, saplogon):
    """Launch SAPLogon application"""

    utilities.launch_saplogon_with_params(saplogon if saplogon else ctx.obj.config.saplogon_path)


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
@click.option('-time', "--timeout", "timeout", default=utilities.default_time_to_wait_for_web(), show_default=True,
              type=click.INT, help='Timer in seconds to wait web site to load')
@click.option("-n", "--new", "reuse", help="Flag. Defines whether a new connection to an SAP is reused",
              default=False, is_flag=True, show_default=True)
@click.pass_context
def run(ctx, system: str, mandant: int, user: str, customer: str, description: str, external_user: bool,
        language: str, guiparm: str, snc_name: str, snc_qop: str, transaction: str, system_command: str, report: str,
        parameter: str, web: bool, timeout: int, reuse: bool):
    """
    \b
    Launch SAP system \n
    \b
    Optional arguments:
    1. SYSTEM: Request a SAP system by system id
    2. MANDANT: Request a SAP system by mandant/client
    """

    if snc_name is not None and snc_qop is None or snc_name is None and snc_qop is not None:
        utilities.print_message("\nBoth parameters must be used: -sname/--snc_name and -sqop/--snc_qop",
                                utilities.message_type_warning)
        raise click.Abort

    query_result = ctx.invoke(list_systems, system=system, mandant=mandant, user=user, customer=customer,
                              description=description,
                              url=web, verbose=False, enum=True)
    if not query_result:
        return
    # --------------------------
    selected_sap_systems = [
        Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
        for item in query_result]

    if language is None:
        language = ctx.obj.config.language

    selected_system = utilities.choose_system(selected_sap_systems)

    if web:
        if selected_system.url != "":
            utilities.print_message(
                f"Launching web site: {selected_system.url} ({selected_system.description} of {selected_system.customer})",
                message_type=utilities.message_type_message)

            utilities.open_url(f"{selected_system.url}")

            utilities.print_message(
                f"Waiting web site to load: {timeout if timeout else ctx.obj.config.wait_site_to_load} seconds",
                utilities.message_type_message)

            time.sleep(timeout if timeout else ctx.obj.config.wait_site_to_load)

            logger.info(f"Autotype sequence: {selected_system.autotype}")
            utilities.launch_autotype_sequence(selected_system.autotype, selected_system.user, selected_system.password)

        else:
            no_system_found = Sap_system(system.upper() if system else None,
                                         str(mandant).zfill(3) if mandant else None,
                                         user.upper() if user else None, None,
                                         customer.upper() if customer else None,
                                         description.upper() if description else None,
                                         None, None)

            utilities.print_system_list(no_system_found, title="NO URL FOUND according to search criteria",
                                        color=utilities.color_warning, url=True)
            raise click.Abort
    else:

        argument, selected_system, command, command_type = utilities.prepare_parameters_to_launch_system(
            selected_system, language,
            external_user,
            guiparm, snc_name, snc_qop,
            transaction, parameter, report, system_command, reuse,
            ctx.obj.config.command_line_path)

        if external_user:
            message = "Trying to LAUNCH the following system with EXTERNAL USER"
        else:
            message = "Trying to LAUNCH the following system "

        utilities.print_system_list(selected_system, title=message,
                                    command=command, command_type=command_type)

        logger.info(f"{argument}")

        # SAP Launching
        utilities.open_sap(argument)


@sap_cli.command("debug", short_help="System debug: either create debug file or start system debugging")
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
    2. Start debugging of the opened system (the last used windows will be used): run 'sap debug <system> <mandant>'
    \b
    Optional arguments:
    1. SYSTEM: Request a SAP system by system
    2. MANDANT: Request a SAP system by mandant/client
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
        if not query_result:
            return

        # --------------------------
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            for item in query_result]

        if language is None:
            language = ctx.obj.config.language

        # As soon as debugger stops working - revert all the changes to "prepare_parameters_to_launch_system"
        #  as it influence whether to open new windows, or to debug the latest opened. All arguments
        #  value must be entered
        selected_system = utilities.choose_system(selected_sap_systems)
        try:
            argument, selected_system, command, command_type = utilities.prepare_parameters_to_launch_system(
                selected_system, language,
                None, guiparm, snc_name,
                snc_qop, None, None, None, None, None,
                ctx.obj.config.command_line_path)
        except WrongPath as err:
            click.echo(f"{err}")
            raise click.Abort

        argument = argument + " -command=/H" + " -type=SystemCommand"

        utilities.print_system_list(selected_system, title="Trying to DEBUG the following system")

        logger.info(f"{argument}")

        utilities.open_sap(argument)


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
    if query_result:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            for item in query_result]

        if language is None:
            language = ctx.obj.config.language

        selected_system = utilities.choose_system(selected_sap_systems)
        try:
            argument, selected_system, command, command_type = utilities.prepare_parameters_to_launch_system(
                selected_system, language, None,
                None, None, None, None, None, None, None, None,
                ctx.obj.config.command_line_path)

        except WrongPath as err:
            click.echo(f"{err}")
            raise click.Abort

        argument = argument + " -command=?STAT" + " -type=SystemCommand"

        utilities.print_system_list(selected_system, title="Opening STATUS of the following system")

        logger.info(f"{argument}")

        utilities.open_sap(argument)


@sap_cli.command("pw")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option('--clear/--no_clear', "clear_clipboard", is_flag=True, default=True,
              help='Clear clipboard', show_default=True)
@click.option('-time', "--timeout", "timeout", default=utilities.default_time_to_clear(), show_default=True,
              type=click.INT, help='Timer in seconds to clear clipboard')
@click.pass_context
def copy_password(ctx, system: str, mandant: int, user: str, customer: str, description: str, clear_clipboard: bool,
                  timeout: int):
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
    if query_result:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            for item in query_result]

        selected_system = utilities.choose_system(selected_sap_systems)

        pyperclip.copy(selected_system.password)

        utilities.print_message("Password is copied into clipboard.", message_type=utilities.message_type_message)

        if clear_clipboard:
            utilities.print_message(
                "If you use Clipboard managers, you should add PY.EXE, CMD.EXE applications to the exclusion list,\nin order to keep sensitive information safe from copying to clipboard manager.",
                message_type=utilities.message_type_sensitive)

            utilities.print_message(f"Clipboard will be cleared in {timeout} seconds.",
                                    message_type=utilities.message_type_message)

            try:
                utilities.countdown(timeout)
            except KeyboardInterrupt:
                click.echo("\n")
                utilities.print_message("Aborted",
                                        message_type=utilities.message_type_error)
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()

            click.echo("\n")
            utilities.print_message("Clipboard is cleared.", message_type=utilities.message_type_message)


@sap_cli.command("add")
@click.pass_context
@click.option("-system", prompt=True, help="System Id", type=utilities.LETTERS_NUMBERS_3)
@click.option("-mandant", prompt=True, help="Mandant/Client number", type=click.IntRange(1, 999))
@click.option("-user", prompt=True, help="User")
@click.option("-password", help="Password", prompt=True, confirmation_prompt=True, hide_input=True)
@click.option("-customer", prompt=True, help="Customer name", type=click.STRING, default="")
@click.option("-description", prompt=True, help="SAP system description", type=click.STRING, default="")
@click.option("-url", prompt=True, help="SAP system Url", type=click.STRING, default="")
@click.option("-autotype", prompt=True, help="Autotype sequence for logining to web site", type=click.STRING,
              default=utilities.default_sequence(), show_default=True)
@click.option("-v", "--verbose", "verbose", help="Flag. Show passwords for selected systems", is_flag=True,
              default=False)
@click.option("-time", "--timeout", "timeout", help="Timeout to clear passwords from screen if '-v' option is used",
              type=click.INT, default=0)
def add(ctx, system: str, mandant: str, user: str, password: str, description: str, customer: str, url: str,
        autotype: str, verbose: bool, timeout: int):
    """
    Add sap system with its parameters to db. Just run 'sap add' and follow instructions.
    """

    with _sap_db(ctx.obj.config):
        encrypted_password = ctx.obj.crypto.encrypto(str.encode(password))
        sap_system = Sap_system(
            str(system).upper(),
            str(mandant).zfill(3),
            str(user).upper(),
            encrypted_password,
            str(customer),
            str(description),
            str(url),
            str(autotype)
        )
        result = sap.add(sap_system)

        if result is not None:
            utilities.print_message("Failed to add system to database ... \n",
                                    message_type=utilities.message_type_sensitive)
            click.echo(result)
        else:
            sap_system = Sap_system(str(system).upper() if system else None, str(mandant) if mandant else None,
                                    user.upper() if user else None)
            result = sap.query_system(sap_system)

            added_system = [Sap_system(item[0], item[1], item[2], ctx.obj.crypto.decrypto(item[3]), item[4],
                                       item[5], item[6], item[7]) for item in result]
            utilities.print_system_list(*added_system, title="The following system is ADDED to the database: ",
                                        verbose=verbose,
                                        timeout=timeout if timeout else ctx.obj.config.time_to_clear)


@sap_cli.command("update", short_help="Update record from database")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option("-v", "--verbose", "verbose", help="Show passwords for selected systems", is_flag=True, default=False)
@click.option("-time", "--timeout", "timeout", help="Timeout to clear passwords from screen if '-v' option is used",
              type=click.INT, default=0)
@click.pass_context
def update(ctx, system: str, mandant: str, user: str, customer: str, description: str, verbose: bool, timeout: int):
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
    if query_result:
        selected_sap_systems = [Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
                                for item in query_result]

        selected_system = utilities.choose_system(selected_sap_systems)

        # TODO: попробовать переделать на
        #  password = getpass.getpass("Enter password for external user: ")
        #  если пользователь нажимает ENTER, а поле пустое, то запрашивать хочет ли он оставить старый пароль

        password_new = click.prompt("\nEnter new password", default=selected_system.password)
        customer_new = click.prompt("Enter Customer", default=selected_system.customer)
        description_new = click.prompt("Enter system description", default=selected_system.description)
        url_new = click.prompt("Enter URL", default=selected_system.url)
        autotype_new = click.prompt("Enter Autotype sequence", default=selected_system.autotype)

        sap_encrypted_system = Sap_system(
            str(selected_system.system).upper(),
            str(selected_system.mandant).zfill(3),
            str(selected_system.user).upper(),
            ctx.obj.crypto.encrypto(str.encode(password_new)),
            str(customer_new),
            str(description_new),
            str(url_new),
            str(autotype_new),
        )

        with _sap_db(ctx.obj.config):
            result = sap.update(sap_encrypted_system)

            if result is None:
                result = sap.query_system(sap_encrypted_system)

                updated_system = [
                    Sap_system(item[0], item[1], item[2], ctx.obj.crypto.decrypto(item[3]), item[4], item[5], item[6],
                               item[7]) for item in result]

                utilities.print_system_list(*updated_system, title="The following system is UPDATED", verbose=verbose,
                                            timeout=timeout if timeout else ctx.obj.config.time_to_clear)
            else:
                no_system_found = Sap_system(system.upper() if system else None,
                                             str(mandant).zfill(3) if mandant else None,
                                             user.upper() if user else None,
                                             None,
                                             customer.upper() if customer else None,
                                             description.upper() if description else None,
                                             None, None)

                utilities.print_system_list(no_system_found, title="FAILED TO UPDATE the following system",
                                            color=utilities.color_warning)


@sap_cli.command("delete")
@click.argument("system", required=False, type=click.STRING)
@click.argument("mandant", required=False, type=click.IntRange(1, 999))
@click.option("-u", "--user", "user", help="Request a SAP system by user")
@click.option("-c", "--customer", "customer", help="Request a SAP system by customer", type=click.STRING)
@click.option("-d", "--description", "description", help="Request a SAP system by description", type=click.STRING)
@click.option("-confirm", "--confirm", "confirm", help="Confirm delete command", is_flag=True, default=False,
              show_default=True)
@click.pass_context
def delete(ctx, system: str, mandant: str, user: str, customer: str, description: str, confirm):
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
    if query_result:
        selected_sap_systems = [
            Sap_system(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            for item in query_result]

        selected_system = utilities.choose_system(selected_sap_systems)

        message = "Trying to DELETE the following system"
        utilities.print_system_list(selected_system, title=message)

        if not confirm:
            click.confirm(click.style('\nDo you really want to delete the system?', **utilities.color_sensitive),
                          abort=True, default=confirm)

        system_to_delete = Sap_system(selected_system.system,
                                      selected_system.mandant,
                                      selected_system.user,
                                      selected_system.password,
                                      selected_system.customer,
                                      selected_system.description,
                                      selected_system.url)

        with _sap_db(ctx.obj.config):
            sap.delete(system_to_delete)

            result = sap.query_system(system_to_delete)

            if not result:

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
              help='Create config file. For technical purpose. Use "sap start" to create config')
@click.option('-open', is_flag=True, callback=open_config, expose_value=False, is_eager=True,
              help='Open config file')
@click.option('-folder', is_flag=True, callback=open_folder, expose_value=False, is_eager=True,
              help='Open config folder')
@click.pass_context
def config(ctx):
    """ Config file creation or editing """

    config_markdown = """
    Enter one of subcommands:

    \t -create       Create config file. For technical purpose. Use "sap start" to create config
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
@click.option("-url", "--show_url", "url", help="Flag. Display url of the requested SAP system", is_flag=True,
              default=False, show_default=True)
@click.option("-v", "--verbose", "verbose", help="Flag. Display passwords of the requested SAP system", is_flag=True,
              default=False, show_default=True)
@click.option("-time", "--timeout", "timeout", help="Timeout to clear passwords from screen if '-v' option is used",
              type=click.INT, default=0)
@click.option("-e", "--enum", "enum", help="Flag. Enumerate systems", is_flag=True, default=False, show_default=True)
@click.pass_context
def list_systems(ctx, system: str, mandant: int, user: str, customer: str, description: str, url: bool,
                 verbose: bool, timeout: int, enum: bool) -> list:
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

    sap_system = []

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
                                        color=utilities.color_warning)
        else:
            sap_system = [
                Sap_system(item[0], item[1], item[2], ctx.obj.crypto.decrypto(item[3]), item[4], item[5], item[6],
                           item[7])
                for item in result]

            utilities.print_system_list(*sap_system, title="Available systems", verbose=verbose,
                                        timeout=timeout if timeout else ctx.obj.config.time_to_clear, url=url,
                                        enum=enum)

        return sap_system if sap_system else []


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


@sap_cli.command("start", short_help="Starting point for working with SAP command line tool")
@click.option('-skip_message', '--skip_message', 'skip_message', is_flag=True, default=False,
              help="Skip result message")
@click.pass_context
def start(ctx, skip_message):
    """
    \b
    Starting point for working with SAP command line tool
    1. Database creation.
    2. ini file with config parameters creation.
    3. Private and public encryption keys.
    4. Useful messages.
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

    if not skip_message:
        folder = Path(__file__)
        filename = 'start.md'
        path = folder.parent / filename
        start_markdown_text = ""

        with open(path, mode='rt', encoding='utf-8') as file:
            start_markdown_text += str(file.read())

        console = Console()
        markdown_text = Markdown(str(start_markdown_text))
        console.print(markdown_text)

        click.pause('\nPress enter to open files folder and start working. Good luck.')

        click.launch(ctx.obj.config.config_file_path, locate=True)


@sap_cli.command("backup", short_help="Create backup")
@click.option("-password", help="Password for backup", prompt=True, confirmation_prompt=True, hide_input=True,
              type=utilities.PASS_REQUIREMENT)
@click.option('-skip_message', '--skip_message', 'skip_message', is_flag=True, default=False,
              help="Skip result message")
@click.pass_context
def backup(ctx, password, skip_message):
    """
    \b
    Create backup for the following files:
    1. list of saplogon systems (SAPUILandscape.xml)
    2. database
    3. encryption keys (private and public)
    4. sap_config.ini
    """

    # -------------------------------------------
    # Files to archive:
    # -------------------------------------------

    #  Paths to SAPUILandscape.xml: https://launchpad.support.sap.com/#/notes/2075150
    saplogon_ini_path = os.path.join(os.path.expandvars(r'%APPDATA%\SAP\Common'), SAPLOGON_INI)

    file_list = [
        ctx.obj.config.db_path,
        ctx.obj.config.public_key_path,
        ctx.obj.config.private_key_path,
        ctx.obj.config.config_file_path,
        saplogon_ini_path,
    ]
    # -------------------------------------------

    cofig_file_folder = ctx.obj.config.config_path

    backup_obj = Backup(password, cofig_file_folder, file_list)
    back_path = backup_obj.create()

    if os.path.exists(back_path):
        if not skip_message:
            utilities.print_message(f'Backup successfully created: {back_path}',
                                    message_type=utilities.message_type_message)
            click.launch(url=back_path, locate=True)
        else:
            click.echo(backup_obj.backup_file_path)
    else:
        utilities.print_message('Backup creation failed', message_type=utilities.message_type_error)
        click.echo()


@sap_cli.command("parlist")
@click.option("-t", "--transaction", "transaction", help="Transaction code", type=click.STRING)
@click.option("-e", "--enum", "enum", help="Flag. Enumerate systems", is_flag=True, type=click.BOOL, default=False)
@click.pass_context
def parameter_list(ctx, transaction, enum):
    """
    List transaction's parameter from database 'Parameters'
    """

    param = Parameter(str(transaction).upper() if transaction else None, None)

    with _sap_db(ctx.obj.config):
        result = sap.query_param(param)

        if not result:
            param = Parameter(str(transaction).upper() if transaction else None, None)
            utilities.print_parameters_list(param, title="NOTHING FOUND according to search criteria",
                                            color=utilities.color_warning)
        else:
            parameters = [Parameter(item[0], item[1]) for item in result]
            utilities.print_parameters_list(*parameters, title="Available transactions and parameters", enum=enum)

        return result if result else None


@sap_cli.command("pardel")
@click.option("-t", "--transaction", "transaction", help="Transaction code", type=click.STRING)
@click.option("-confirm", "--confirm", "confirm", help="Confirm delete command", is_flag=True, default=False,
              show_default=True)
@click.pass_context
def parameter_delete(ctx, transaction, confirm):
    """
    Delete transaction's parameter from database 'Parameters'
    """

    # TODO: перед запросом разрешение на удаление нужно вывести систему, которую мы удаляем. как в SAP DEL

    param = Parameter(str(transaction).upper() if transaction else None, None)

    query_result = ctx.invoke(parameter_list, transaction=param.transaction, enum=True)
    # --------------------------
    if query_result:
        selected_parameters = [Parameter(item[0], item[1]) for item in query_result]

        selected_params = utilities.choose_parameter(selected_parameters)

        message = "Trying to DELETE the following transaction and its parameters"
        utilities.print_parameters_list(selected_params, title=message)

        if not confirm:
            click.confirm(click.style('\nDo you really want to delete the system?', **utilities.color_sensitive),
                          abort=True, default=confirm)

        parameter_to_delete = Parameter(selected_params.transaction,
                                        selected_params.parameter)

        with _sap_db(ctx.obj.config):
            sap.delete_param(parameter_to_delete)

            result = sap.query_param(parameter_to_delete)

            if result is not None:

                utilities.print_parameters_list(parameter_to_delete,
                                                title="The following parameter is DELETED from database")
            else:
                no_parameter_found = Parameter(parameter_to_delete.transaction, parameter_to_delete.parameter)

                utilities.print_parameters_list(no_parameter_found, title="FAILED TO UPDATE the following system",
                                                color=utilities.color_warning)


@sap_cli.command("paradd")
@click.option("-t", "--transaction", "transaction", prompt=True, help="Transaction code", type=click.STRING)
@click.option("-p", "--parameter", "parameter", prompt=True, help="Transaction's parameter", type=click.STRING)
@click.pass_context
def parameter_add(ctx, transaction, parameter):
    """
    Add transaction's parameter to database 'Parameters'
    """

    param = Parameter(str(transaction).upper(), str(parameter).upper())

    with _sap_db(ctx.obj.config):
        result = sap.add_param(param)

        if result is not None:
            utilities.print_message("Failed to add system to database ... \n", utilities.message_type_error)
            click.echo(result)
        else:
            ctx.invoke(parameter_list, transaction=param.transaction)


@sap_cli.command("parupdate", short_help="Update record from database")
@click.option("-t", "--transaction", "transaction", help="Transaction code", type=click.STRING)
@click.option("-p", "--parameter", "parameter", prompt=True, help="Transaction's parameter", type=click.STRING)
@click.pass_context
def parameter_update(ctx, transaction: str, parameter: str):
    """
    \b
    Update parameters for selected transaction
    """

    param = Parameter(str(transaction).upper() if transaction else None, None)

    query_result = ctx.invoke(parameter_list, transaction=param.transaction, enum=True)
    # --------------------------
    if query_result:
        selected_parameters = [Parameter(item[0], item[1]) for item in query_result]

        selected_params = utilities.choose_parameter(selected_parameters)

        parameter_new = parameter if parameter else click.prompt(
            f"\nEnter new parameters for transaction {selected_params.transaction}",
            default=selected_params.parameter)

        parameter_updated = Parameter(selected_params.transaction, str(parameter_new).upper())

        with _sap_db(ctx.obj.config):
            result = sap.update_param(parameter_updated)

            if result is None:

                utilities.print_parameters_list(parameter_updated,
                                                title="The following system is UPDATED")
            else:
                no_parameter_found = Parameter(parameter_updated.transaction, parameter_updated.parameter)

                utilities.print_parameters_list(no_parameter_found, title="FAILED TO UPDATE the following system",
                                                color=utilities.color_warning)


@contextmanager
def _sap_db(cfg):
    sap.start_sap_db(cfg.db_path, cfg.db_type)
    yield
    sap.stop_sap_db()


if __name__ == "__main__":
    sap_cli()
