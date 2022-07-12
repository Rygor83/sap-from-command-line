#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Command Line Tests for main commands: add, list, delete, update """

import click
import os
import sys
import pyperclip
import pytest
from pytest_mock import mocker  # do not delete it
from rich import print

from sap.api import DEBUG_FILE_NAME, CONFIG_NAME, PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, DATABASE_NAME
from sap.cli import sap_cli
from sap import Sap_system
import sap.utilities

PASSWORD = '12345678'
UPDATED_PASSWORD = '1029384756'

# TODO: нужно попробовать сделать тест без базы данных - чтобы попасть на сообщение об ошибке

sap_system_zzz = sap.Sap_system(system='ZZZ', mandant='999', user='USER25', password=PASSWORD, customer='Roga & copyta',
                                description='Develop')
sap_system_yyy = sap.Sap_system(system='YYY', mandant='998', user='USER21', password=PASSWORD, customer='Vasya Pupkin',
                                description='Production', url='www.vasyapupkin.by',
                                autotype='{USERNAME}{TAB}{PASSWORD}{ENTER}')
sap_system_xxx = sap.Sap_system(system='XXX', mandant='100', user='USER15', password=PASSWORD, customer='XYZ systems',
                                description='Test', url='www.XYZsystems.by',
                                autotype='{USERNAME}{TAB}{PASSWORD}{ENTER}')


def test_start_cli(temp_start_cli):
    """
    Test START command: 'start' command works in temp_start_cli fixture. All we need is to check if files are created
    'sap start'
    """
    assert os.path.exists(os.path.join(temp_start_cli, CONFIG_NAME)) and os.path.exists(
        os.path.join(temp_start_cli, PUBLIC_KEY_NAME)) and os.path.exists(
        os.path.join(temp_start_cli, PRIVATE_KEY_NAME)) and os.path.exists(
        os.path.join(temp_start_cli, DATABASE_NAME))


def test_add_system_1(runner, temp_start_cli):
    """
    Test ADD command: new system 1, basic fields
    'sap add'
    """
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli,
                                 "add",
                                 "-system", sap_system_zzz.system,
                                 "-mandant", sap_system_zzz.mandant,
                                 "-user", sap_system_zzz.user,
                                 "-password", sap_system_zzz.password,
                                 "-customer", sap_system_zzz.customer,
                                 "-description", sap_system_zzz.description,
                                 "-url", sap_system_zzz.url if sap_system_zzz.url else "",
                                 "-autotype", sap_system_zzz.autotype if sap_system_zzz.autotype else ""])
    assert result.output == ('\n\n'
                             '          \x1b[32m\x1b[40mThe following system is ADDED to the database: \x1b[0m           \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_add_system_2_with_url(runner, temp_start_cli):
    """
    Test ADD command: new system 2, basic fields + url, autotype
    'sap add'
    """
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli,
                                 "add",
                                 "-system", sap_system_yyy.system,
                                 "-mandant", sap_system_yyy.mandant,
                                 "-user", sap_system_yyy.user,
                                 "-password", sap_system_yyy.password,
                                 "-customer", sap_system_yyy.customer,
                                 "-description", sap_system_yyy.description,
                                 "-url", sap_system_yyy.url,
                                 "-autotype", sap_system_yyy.autotype])
    assert result.output == ('\n\n'
                             '          \x1b[32m\x1b[40mThe following system is ADDED to the database: \x1b[0m           \n'
                             '┌────────────────────┬────────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer           │ System     │ Mandant     │ Description      │ User     │\n'
                             '╞════════════════════╪════════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ VASYA PUPKIN       │ YYY        │ 998         │ Production       │ USER21   │\n'
                             '└────────────────────┴────────────┴─────────────┴──────────────────┴──────────┘\n')


def test_add_system_3_verbose(runner, temp_start_cli):
    """
    Test ADD command: new system 3, basic fields + url, autotype + show password
    'sap add -v'
    """
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli,
                                 "add",
                                 "-system", sap_system_xxx.system,
                                 "-mandant", sap_system_xxx.mandant,
                                 "-user", sap_system_xxx.user,
                                 "-password", sap_system_xxx.password,
                                 "-customer", sap_system_xxx.customer,
                                 "-description", sap_system_xxx.description,
                                 "-url", sap_system_xxx.url,
                                 "-autotype", sap_system_xxx.autotype,
                                 "-v",
                                 "-time", "1"])
    assert result.output == ('\n\n'
                             '          \x1b[32m\x1b[40mThe following system is ADDED to the database: \x1b[0m           \n'
                             '┌────────────────┬──────────┬───────────┬───────────────┬─────────┬───────────┐\n'
                             '│ Customer       │ System   │ Mandant   │ Description   │ User    │ Password  │\n'
                             '╞════════════════╪══════════╪═══════════╪═══════════════╪═════════╪═══════════╡\n'
                             '│ XYZ SYSTEMS    │ XXX      │ 100       │ Test          │ USER15  │ 12345678  │\n'
                             '└────────────────┴──────────┴───────────┴───────────────┴─────────┴───────────┘\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Information about passwords will be deleted from screen in 1                │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             '\r\x1b[K\r1\r\x1b[K\r0')


def test_list_existing_systems_cli(runner, temp_start_cli):
    """
    Test LIST command: list all available systems
    'sap list'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '│ VASYA PUPKIN        │ YYY       │ 998         │ Production       │ USER21   │\n'
                             '│ XYZ SYSTEMS         │ XXX       │ 100         │ Test             │ USER15   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_systems_show_passwords_cli(runner, temp_start_cli):
    """
    Test LIST command: list all available systems and show passwords
    'sap list -v'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-v", "-time", "1"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────────────────┬─────────┬───────────┬───────────────┬─────────┬──────────┐\n'
                             '│ Customer         │ System  │ Mandant   │ Description   │ User    │ Password │\n'
                             '╞══════════════════╪═════════╪═══════════╪═══════════════╪═════════╪══════════╡\n'
                             '│ ROGA & COPYTA    │ ZZZ     │ 999       │ Develop       │ USER25  │ 12345678 │\n'
                             '│ VASYA PUPKIN     │ YYY     │ 998       │ Production    │ USER21  │ 12345678 │\n'
                             '│ XYZ SYSTEMS      │ XXX     │ 100       │ Test          │ USER15  │ 12345678 │\n'
                             '└──────────────────┴─────────┴───────────┴───────────────┴─────────┴──────────┘\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Information about passwords will be deleted from screen in 1                │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             '\r\x1b[K\r1\r\x1b[K\r0')


def test_list_existing_system_with_system_mandant_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific system and mandant
    'sap list system_id mandant'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "zzz", "999"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_system_only_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific system only
    'sap list system_id'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "zzz"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_mandant_only_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific mandant
    'sap list % mandant'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "%", "999"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_only_partial_mandant_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific partial mandant
    'sap list % mandant'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "%", "99"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '│ VASYA PUPKIN        │ YYY       │ 998         │ Production       │ USER21   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_customer_name_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific customer name
    'sap list -c customer_name'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-c", "roga"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_partial_customer_name_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific partial customer name
    'sap list -c customer_name'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-c", "ro%co"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_user_name_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific username
    'sap list -u username'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-u", "user21"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌────────────────────┬────────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer           │ System     │ Mandant     │ Description      │ User     │\n'
                             '╞════════════════════╪════════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ VASYA PUPKIN       │ YYY        │ 998         │ Production       │ USER21   │\n'
                             '└────────────────────┴────────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_partial_user_name_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific partial username
    'sap list -u username'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-u", "user2"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '│ VASYA PUPKIN        │ YYY       │ 998         │ Production       │ USER21   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_system_description_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific system description
    'sap list -d system_description'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-d", "dev"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Develop          │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_list_existing_system_with_url_cli(runner, temp_start_cli):
    """
    Test LIST command: list system with specific system and show url, autotype information
    'sap list system_id -url'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "yyy", "-url"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌───────────┬────────┬─────────┬────────────┬────────┬───────────┬────────────┐\n'
                             '│           │        │         │            │        │           │ Autotype   │\n'
                             '│ Customer  │ System │ Mandant │ Descripti… │ User   │ URL       │ sequence   │\n'
                             '╞═══════════╪════════╪═════════╪════════════╪════════╪═══════════╪════════════╡\n'
                             '│ VASYA     │ YYY    │ 998     │ Production │ USER21 │ www.vasy… │ {USERNAME… │\n'
                             '│ PUPKIN    │        │         │            │        │           │            │\n'
                             '└───────────┴────────┴─────────┴────────────┴────────┴───────────┴────────────┘\n')


def test_list_existing_systems_enumerated_cli(runner, temp_start_cli):
    """
    Test LIST command: list enumerated all systems
    'sap list --enum'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "--enum"])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────┬───────────────────┬──────────┬────────────┬────────────────┬─────────┐\n'
                             '│ Id   │ Customer          │ System   │ Mandant    │ Description    │ User    │\n'
                             '╞══════╪═══════════════════╪══════════╪════════════╪════════════════╪═════════╡\n'
                             '│ 1    │ ROGA & COPYTA     │ ZZZ      │ 999        │ Develop        │ USER25  │\n'
                             '│ 2    │ VASYA PUPKIN      │ YYY      │ 998        │ Production     │ USER21  │\n'
                             '│ 3    │ XYZ SYSTEMS       │ XXX      │ 100        │ Test           │ USER15  │\n'
                             '└──────┴───────────────────┴──────────┴────────────┴────────────────┴─────────┘\n')


def test_list_no_existing_systems_cli(runner, temp_start_cli):
    """
    Test LIST command: Request for a non-existent system
    'sap list non_existent_system_id'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "bbb"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────┬─────────────┬───────────────┬────────────────────┬─────────┐\n'
                             '│ Customer       │ System      │ Mandant       │ Description        │ User    │\n'
                             '╞════════════════╪═════════════╪═══════════════╪════════════════════╪═════════╡\n'
                             '│                │ BBB         │               │                    │         │\n'
                             '└────────────────┴─────────────┴───────────────┴────────────────────┴─────────┘\n')


def test_pw_no_clipboard_clear_cli(runner, temp_start_cli):
    """
    Test PW command: copying password into clipboard. For this test we do not clear clipboard.
    'sap pw system_id'
    """
    runner.invoke(sap_cli,
                  args=["--config_path", temp_start_cli,
                        "pw", "zzz", "--no_clear"])
    password_from_database = pyperclip.paste()

    assert password_from_database == PASSWORD


def test_pw_clipboard_clear_cli(runner, temp_start_cli):
    """
    Test PW command: copying password into clipboard. And clear clipboard.
    'sap pw system_id'
    """
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "pw", "zzz", "--clear", "-time", "1"])

    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────┬───────────────────┬──────────┬────────────┬────────────────┬─────────┐\n'
                             '│ Id   │ Customer          │ System   │ Mandant    │ Description    │ User    │\n'
                             '╞══════╪═══════════════════╪══════════╪════════════╪════════════════╪═════════╡\n'
                             '│ 1    │ ROGA & COPYTA     │ ZZZ      │ 999        │ Develop        │ USER25  │\n'
                             '└──────┴───────────────────┴──────────┴────────────┴────────────────┴─────────┘\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Password is copied into clipboard.                                          │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             '┌─ Sensitive ─────────────────────────────────────────────────────────────────┐\n'
                             '│ If you use Clipboard managers, you should add PY.EXE, CMD.EXE applications  │\n'
                             '│ to the exclusion list,                                                      │\n'
                             '│ in order to keep sensitive information safe from copying to clipboard       │\n'
                             '│ manager.                                                                    │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Clipboard will be cleared in 1 seconds.                                     │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             '\r\x1b[K\r1\r\x1b[K\r0\n\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Clipboard is cleared.                                                       │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n')


def test_pw_no_existing_system_cli(runner, temp_start_cli):
    """
    Test PW command: Request for a non-existent system to get password
    'sap pw non_existent_system_id'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "pw", "bbb"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────┬─────────────┬───────────────┬────────────────────┬─────────┐\n'
                             '│ Customer       │ System      │ Mandant       │ Description        │ User    │\n'
                             '╞════════════════╪═════════════╪═══════════════╪════════════════════╪═════════╡\n'
                             '│                │ BBB         │               │                    │         │\n'
                             '└────────────────┴─────────────┴───────────────┴────────────────────┴─────────┘\n')


def stub_open_sap(arguments):
    """
    Stab function to replace utilities.open_sap
    """
    print(arguments)


def test_run_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", sap_system_yyy.system])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -reuse=1')


def test_run_existing_system_with_user_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", "-u", sap_system_yyy.user])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -reuse=1')


def test_run_existing_system_new_window_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-n"])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -reuse=0')


def test_run_existing_system_english_language_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    language = 'EN'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-l", language])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language={language} -maxgui -reuse=1')


def test_run_existing_system_external_user_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    external_user = 'EXT123'
    external_password = '123'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-eu"],
                           input=f"{external_user}\n{external_password}\n")
    assert str(result.output).replace("\n", "") == (
        f'Enter external user id: Warning: Password input may be echoed.Enter password for external user: "path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={external_user} -pw={external_password} -language=RU -maxgui -reuse=1')


def test_run_existing_system_with_transaction_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    transaction_code = 'SE11'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-t", transaction_code])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -type=transaction -command={transaction_code} -reuse=1')


def test_run_existing_system_with_transaction_and_parameter_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    Parameter info for transaction is taken from parameters tests
    'sap run system_id'
    """
    transaction_code = 'SM30'
    view_name = 'V_T001'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-t",
                                 transaction_code, "-p", view_name])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -type=transaction -command="*{transaction_code} VIEWNAME={view_name};" -reuse=1')


def test_run_existing_system_with_transaction_and_parameter_show_log_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    !!! Parameter info for transaction is taken from parameters tests: test_1_param_commands_cli.py
    'sap run system_id'
    """
    transaction_code = 'SM30'
    view_name = 'V_T001'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap',
                        return_value=True)  # We do not use stab function as we get info from log "--log_level DEBUG"
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "--log_level", "DEBUG", "run", sap_system_yyy.system,
                                 "-t", transaction_code, "-p", view_name])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -type=transaction -command="*{transaction_code} VIEWNAME={view_name};" -reuse=1')


def test_run_existing_system_with_system_command_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    system_command = '/nex'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-s", system_command])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -type=SystemCommand -command={system_command} -reuse=1')


def test_run_existing_system_with_report_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    report_name = 'RFITEMGL'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-r", report_name])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -type=report -command={report_name} -reuse=1')


def stub_launch(url=''):
    """
    Stab function to replace click.launch for launching web sites
    """
    return 0 if url else 1


def test_run_web_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: Request for a non-existent system's web version
    'sap run system_id -w'
    """
    mocker.patch.object(sap.utilities, 'open_url', return_value=True)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_yyy.system, "-w", "-time", '1'])
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌────┬──────────┬────────┬─────────┬──────────┬────────┬───────────┬──────────┐\n'
                             '│    │          │        │         │          │        │           │ Autotype │\n'
                             '│ Id │ Customer │ System │ Mandant │ Descrip… │ User   │ URL       │ sequence │\n'
                             '╞════╪══════════╪════════╪═════════╪══════════╪════════╪═══════════╪══════════╡\n'
                             '│ 1  │ VASYA    │ YYY    │ 998     │ Product… │ USER21 │ www.vasy… │ {USERNA… │\n'
                             '│    │ PUPKIN   │        │         │          │        │           │          │\n'
                             '└────┴──────────┴────────┴─────────┴──────────┴────────┴───────────┴──────────┘\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Launching web site: www.vasyapupkin.by (Production of VASYA PUPKIN)         │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Waiting web site to load: 1 seconds                                         │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n')


def test_run_web_existing_system_without_url_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: Request for a non-existent system's web version
    'sap run system_id -w'
    """
    mocker.patch.object(click, 'launch', return_value="")
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", sap_system_zzz.system, "-w"])

    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌────┬────────────┬────────┬─────────┬────────────┬────────┬─────┬────────────┐\n'
                             '│    │            │        │         │            │        │     │ Autotype   │\n'
                             '│ Id │ Customer   │ System │ Mandant │ Descripti… │ User   │ URL │ sequence   │\n'
                             '╞════╪════════════╪════════╪═════════╪════════════╪════════╪═════╪════════════╡\n'
                             '│ 1  │ ROGA &     │ ZZZ    │ 999     │ Develop    │ USER25 │     │            │\n'
                             '│    │ COPYTA     │        │         │            │        │     │            │\n'
                             '└────┴────────────┴────────┴─────────┴────────────┴────────┴─────┴────────────┘\n'
                             '\n\n'
                             '             \x1b[33m\x1b[40mNO URL FOUND according to search criteria\x1b[0m              \n'
                             '┌───────────┬────────┬─────────┬─────────────┬──────┬─────┬───────────────────┐\n'
                             '│ Customer  │ System │ Mandant │ Description │ User │ URL │ Autotype sequence │\n'
                             '╞═══════════╪════════╪═════════╪═════════════╪══════╪═════╪═══════════════════╡\n'
                             '│           │ ZZZ    │         │             │      │     │                   │\n'
                             '└───────────┴────────┴─────────┴─────────────┴──────┴─────┴───────────────────┘\n'
                             'Aborted.\n')


def test_run_web_no_existing_system_cli(runner, temp_start_cli):
    """
    Test RUN command: Request for a non-existent system's web version
    'sap run system_id -w'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", "BBB", "-w"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────┬─────────────┬───────────────┬────────────────────┬─────────┐\n'
                             '│ Customer       │ System      │ Mandant       │ Description        │ User    │\n'
                             '╞════════════════╪═════════════╪═══════════════╪════════════════════╪═════════╡\n'
                             '│                │ BBB         │               │                    │         │\n'
                             '└────────────────┴─────────────┴───────────────┴────────────────────┴─────────┘\n')


def test_debug_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test DEBUG command
    'sap debug system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "debug", sap_system_yyy.system])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file" -system={sap_system_yyy.system} -client={sap_system_yyy.mandant} -user={sap_system_yyy.user} -pw={sap_system_yyy.password} -language=RU -maxgui -reuse=1 -command=/H -type=SystemCommand')


def test_debug_file(runner, temp_start_cli):
    """
    Test DEBUG command: create debug file
    'sap debug -f'
    """
    runner.invoke(sap_cli, args=["-path", temp_start_cli, 'debug', '-f', '-o'])
    with open(os.path.join(temp_start_cli, DEBUG_FILE_NAME), mode='r', encoding='utf-8') as file:
        text = file.read()
    assert text == '[FUNCTION]\nCommand =/H\nTitle=Debugger\nType=SystemCommand'


def test_debug_no_existing_system_cli(runner, temp_start_cli):
    """
    Test DEBUG command: Request for a non-existent system to delete
    'sap debug non_existent_system_id'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "debug", "bbb"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────┬─────────────┬───────────────┬────────────────────┬─────────┐\n'
                             '│ Customer       │ System      │ Mandant       │ Description        │ User    │\n'
                             '╞════════════════╪═════════════╪═══════════════╪════════════════════╪═════════╡\n'
                             '│                │ BBB         │               │                    │         │\n'
                             '└────────────────┴─────────────┴───────────────┴────────────────────┴─────────┘\n')


def test_logon_cli(runner, temp_start_cli, mocker):
    """
    Test LOGON command: run saplogon application. For this all we need is to check if application exists.
    click.launch will launch any exe file if it exists.
    'sap logon'
    """

    path_to_test_file = os.path.join(temp_start_cli, CONFIG_NAME)
    mocker.patch.object(click, 'launch', return_value=True)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "logon", "-s", path_to_test_file])

    assert result.output == f"Trying to launch: {path_to_test_file}\n"


def test_logon_wrong_saplogon_path_cli(runner, temp_start_cli):
    """
    Test LOGON command: run saplogon application
    'sap logon'
    """

    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "logon"])
    assert result.output == ('┌─ Error ─────────────────────────────────────────────────────────────────────┐\n'
                             '│                                                                             │\n'
                             '│ SAP executable does not exist: path to saplogon.exe file                    │\n'
                             '│ Check the following path: path to saplogon.exe file                         │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             'Aborted.\n')


def test_update_requesting_system_mandant_cli(runner, temp_start_cli):
    """
    Test UPDATE command: updating specific system
    'sap update system_id mandant'
    """
    result = runner.invoke(sap_cli,
                           args=["-path", temp_start_cli,
                                 "update", "zzz", "999"],
                           input="87654321\n\nDev\n\n\n")
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────┬───────────────────┬──────────┬────────────┬────────────────┬─────────┐\n'
                             '│ Id   │ Customer          │ System   │ Mandant    │ Description    │ User    │\n'
                             '╞══════╪═══════════════════╪══════════╪════════════╪════════════════╪═════════╡\n'
                             '│ 1    │ ROGA & COPYTA     │ ZZZ      │ 999        │ Develop        │ USER25  │\n'
                             '└──────┴───────────────────┴──────────┴────────────┴────────────────┴─────────┘\n'
                             '\n'
                             'Enter new password [12345678]: 87654321\n'
                             'Enter Customer [ROGA & COPYTA]: \n'
                             'Enter system description [Develop]: Dev\n'
                             'Enter URL []: \n'
                             'Enter Autotype sequence []: \n'
                             '\n\n'
                             '                  \x1b[32m\x1b[40mThe following system is UPDATED\x1b[0m                   \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Dev              │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_update_choosing_system_from_list_cli(runner, temp_start_cli):
    """
    Test UPDATE command: choosing system from list to update it
    'sap update'
    """
    result = runner.invoke(sap_cli,
                           args=["-path", temp_start_cli,
                                 "update"],
                           input="2\n\n\nProd\n\n\n")
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────┬───────────────────┬──────────┬────────────┬────────────────┬─────────┐\n'
                             '│ Id   │ Customer          │ System   │ Mandant    │ Description    │ User    │\n'
                             '╞══════╪═══════════════════╪══════════╪════════════╪════════════════╪═════════╡\n'
                             '│ 1    │ ROGA & COPYTA     │ ZZZ      │ 999        │ Dev            │ USER25  │\n'
                             '│ 2    │ VASYA PUPKIN      │ YYY      │ 998        │ Production     │ USER21  │\n'
                             '│ 3    │ XYZ SYSTEMS       │ XXX      │ 100        │ Test           │ USER15  │\n'
                             '└──────┴───────────────────┴──────────┴────────────┴────────────────┴─────────┘\n'
                             '\n\n'
                             'Choose a system you want to login. Available values from 1 to 3: \n'
                             '>>>: \n'
                             'Enter new password [12345678]: \n'
                             'Enter Customer [VASYA PUPKIN]: \n'
                             'Enter system description [Production]: Prod\n'
                             'Enter URL [www.vasyapupkin.by]: \n'
                             'Enter Autotype sequence [{USERNAME}{TAB}{PASSWORD}{ENTER}]: \n'
                             '\n\n'
                             '                  \x1b[32m\x1b[40mThe following system is UPDATED\x1b[0m                   \n'
                             '┌────────────────────┬────────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer           │ System     │ Mandant     │ Description      │ User     │\n'
                             '╞════════════════════╪════════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ VASYA PUPKIN       │ YYY        │ 998         │ Prod             │ USER21   │\n'
                             '└────────────────────┴────────────┴─────────────┴──────────────────┴──────────┘\n')


def test_update_requesting_customer_show_updated_password_cli(runner, temp_start_cli):
    """
    Test UPDATE command: updating specific system searched by customer name and showing updated password
    'sap update -c customer_name -v'
    """
    result = runner.invoke(sap_cli,
                           args=["-path", temp_start_cli,
                                 "update",
                                 "-c", "roga",
                                 "-v", "-time", "1"],
                           input=f"{UPDATED_PASSWORD}\n\n\n\n\n")
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────┬───────────────────┬──────────┬────────────┬────────────────┬─────────┐\n'
                             '│ Id   │ Customer          │ System   │ Mandant    │ Description    │ User    │\n'
                             '╞══════╪═══════════════════╪══════════╪════════════╪════════════════╪═════════╡\n'
                             '│ 1    │ ROGA & COPYTA     │ ZZZ      │ 999        │ Dev            │ USER25  │\n'
                             '└──────┴───────────────────┴──────────┴────────────┴────────────────┴─────────┘\n'
                             '\n'
                             'Enter new password [87654321]: 1029384756\n'
                             'Enter Customer [ROGA & COPYTA]: \n'
                             'Enter system description [Dev]: \n'
                             'Enter URL []: \n'
                             'Enter Autotype sequence []: \n'
                             '\n\n'
                             '                  \x1b[32m\x1b[40mThe following system is UPDATED\x1b[0m                   \n'
                             '┌─────────────────┬─────────┬──────────┬───────────────┬─────────┬────────────┐\n'
                             '│ Customer        │ System  │ Mandant  │ Description   │ User    │ Password   │\n'
                             '╞═════════════════╪═════════╪══════════╪═══════════════╪═════════╪════════════╡\n'
                             f'│ ROGA & COPYTA   │ ZZZ     │ 999      │ Dev           │ USER25  │ {UPDATED_PASSWORD} │\n'
                             '└─────────────────┴─────────┴──────────┴───────────────┴─────────┴────────────┘\n'
                             '┌─ Message ───────────────────────────────────────────────────────────────────┐\n'
                             '│ Information about passwords will be deleted from screen in 1                │\n'
                             '└─────────────────────────────────────────────────────────────────────────────┘\n'
                             '\r\x1b[K\r1\r\x1b[K\r0')


def test_update_no_existing_system_cli(runner, temp_start_cli):
    """
    Test UPDATE command: Request for a non-existent system to update
    'sap update non_existent_system_id'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "update", "bbb"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────┬─────────────┬───────────────┬────────────────────┬─────────┐\n'
                             '│ Customer       │ System      │ Mandant       │ Description        │ User    │\n'
                             '╞════════════════╪═════════════╪═══════════════╪════════════════════╪═════════╡\n'
                             '│                │ BBB         │               │                    │         │\n'
                             '└────────────────┴─────────────┴───────────────┴────────────────────┴─────────┘\n')


def test_delete_existing_system_choosing_from_list_cli(runner, temp_start_cli):
    """
    Test DELETE command: choosing system from list to delete it
    'sap delete'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "delete"], input="3\ny\n")
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────┬───────────────────┬──────────┬────────────┬────────────────┬─────────┐\n'
                             '│ Id   │ Customer          │ System   │ Mandant    │ Description    │ User    │\n'
                             '╞══════╪═══════════════════╪══════════╪════════════╪════════════════╪═════════╡\n'
                             '│ 1    │ ROGA & COPYTA     │ ZZZ      │ 999        │ Dev            │ USER25  │\n'
                             '│ 2    │ VASYA PUPKIN      │ YYY      │ 998        │ Prod           │ USER21  │\n'
                             '│ 3    │ XYZ SYSTEMS       │ XXX      │ 100        │ Test           │ USER15  │\n'
                             '└──────┴───────────────────┴──────────┴────────────┴────────────────┴─────────┘\n'
                             '\n\n'
                             'Choose a system you want to login. Available values from 1 to 3: \n'
                             '>>>: \n\n'
                             '               \x1b[32m\x1b[40mTrying to DELETE the following system\x1b[0m                \n'
                             '┌───────────────────┬────────────┬─────────────┬──────────────────┬───────────┐\n'
                             '│ Customer          │ System     │ Mandant     │ Description      │ User      │\n'
                             '╞═══════════════════╪════════════╪═════════════╪══════════════════╪═══════════╡\n'
                             '│ XYZ SYSTEMS       │ XXX        │ 100         │ Test             │ USER15    │\n'
                             '└───────────────────┴────────────┴─────────────┴──────────────────┴───────────┘\n'
                             '\n'
                             'Do you really want to delete the system? [y/N]: y\n'
                             '\n\n'
                             '           \x1b[32m\x1b[40mThe following system is DELETED from database\x1b[0m            \n'
                             '┌───────────────────┬────────────┬─────────────┬──────────────────┬───────────┐\n'
                             '│ Customer          │ System     │ Mandant     │ Description      │ User      │\n'
                             '╞═══════════════════╪════════════╪═════════════╪══════════════════╪═══════════╡\n'
                             '│ XYZ SYSTEMS       │ XXX        │ 100         │ Test             │ USER15    │\n'
                             '└───────────────────┴────────────┴─────────────┴──────────────────┴───────────┘\n')


def test_delete_existing_system_by_system_id_cli(runner, temp_start_cli):
    """
    Test DELETE command: choosing system by system id to delete it
    'sap delete system_id'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "delete", "zzz"], input="y\n")
    assert result.output == ('\n\n'
                             '                         \x1b[32m\x1b[40mAvailable systems\x1b[0m                          \n'
                             '┌──────┬───────────────────┬──────────┬────────────┬────────────────┬─────────┐\n'
                             '│ Id   │ Customer          │ System   │ Mandant    │ Description    │ User    │\n'
                             '╞══════╪═══════════════════╪══════════╪════════════╪════════════════╪═════════╡\n'
                             '│ 1    │ ROGA & COPYTA     │ ZZZ      │ 999        │ Dev            │ USER25  │\n'
                             '└──────┴───────────────────┴──────────┴────────────┴────────────────┴─────────┘\n'
                             '\n\n'
                             '               \x1b[32m\x1b[40mTrying to DELETE the following system\x1b[0m                \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Dev              │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n'
                             '\n'
                             'Do you really want to delete the system? [y/N]: y\n'
                             '\n\n'
                             '           \x1b[32m\x1b[40mThe following system is DELETED from database\x1b[0m            \n'
                             '┌─────────────────────┬───────────┬─────────────┬──────────────────┬──────────┐\n'
                             '│ Customer            │ System    │ Mandant     │ Description      │ User     │\n'
                             '╞═════════════════════╪═══════════╪═════════════╪══════════════════╪══════════╡\n'
                             '│ ROGA & COPYTA       │ ZZZ       │ 999         │ Dev              │ USER25   │\n'
                             '└─────────────────────┴───────────┴─────────────┴──────────────────┴──────────┘\n')


def test_delete_no_existing_system_cli(runner, temp_start_cli):
    """
    Test DELETE command: Request for a non-existent system to delete
    'sap delete non_existent_system_id'
    """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "delete", "bbb"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────┬─────────────┬───────────────┬────────────────────┬─────────┐\n'
                             '│ Customer       │ System      │ Mandant       │ Description        │ User    │\n'
                             '╞════════════════╪═════════════╪═══════════════╪════════════════════╪═════════╡\n'
                             '│                │ BBB         │               │                    │         │\n'
                             '└────────────────┴─────────────┴───────────────┴────────────────────┴─────────┘\n')
