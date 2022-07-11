#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Command Line Tests for main commands: add, list, delete, update """

import os
import pyperclip
import pytest

from api import DEBUG_FILE_NAME, CONFIG_NAME, PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, DATABASE_NAME
from sap.cli import sap_cli

PASSWORD = '12345678'
UPDATED_PASSWORD = '1029384756'


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
                                 "-system", "zzz",
                                 "-mandant", "999",
                                 "-user", "USER25",
                                 "-password", PASSWORD,
                                 "-customer", "Roga & copyta",
                                 "-description", "Develop",
                                 "-url", " ",
                                 "-autotype", ""])
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
                                 "-system", "yyy",
                                 "-mandant", "998",
                                 "-user", "USER21",
                                 "-password", PASSWORD,
                                 "-customer", "Vasya Pupkin",
                                 "-description", "Production",
                                 "-url", "www.vasyapupkin.by",
                                 "-autotype", "{USERNAME}{TAB}{PASSWORD}{ENTER}"])
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
                                 "-system", "xxx",
                                 "-mandant", "100",
                                 "-user", "USER15",
                                 "-password", PASSWORD,
                                 "-customer", "XYZ systems",
                                 "-description", "Test",
                                 "-url", "www.XYZsystems.by",
                                 "-autotype", "{USERNAME}{TAB}{PASSWORD}{ENTER}",
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


def test_debug_file(runner, temp_start_cli):
    """
    Test DEBUG command: create debug file
    'sap debug -f'
    """
    runner.invoke(sap_cli, args=["-path", temp_start_cli, 'debug', '-f', '-o'])
    with open(os.path.join(temp_start_cli, DEBUG_FILE_NAME), mode='r', encoding='utf-8') as file:
        text = file.read()
    assert text == '[FUNCTION]\nCommand =/H\nTitle=Debugger\nType=SystemCommand'


@pytest.mark.skip
def test_debug_existing_system_cli(runner, temp_start_cli):
    """
    Test DEBUG command
    'sap debug system_id'
    """
    # TODO: возможно нужно просто проверять саму команду для запуска дебага системы. Вопрос как это сделать ?
    pass


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
                             'Enter URL [ ]: \n'
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
                             'Enter URL [ ]: \n'
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


@pytest.mark.skip
def test_run_existing_system_cli(runner, temp_start_cli):
    """
    Test RUN command: run specific system
    'sap run system_id'
    """
    # TODO: возможно нужно просто проверять саму команду для запуска системы. Вопрос как это сделать ?
    pass


@pytest.mark.skip
def test_logon_cli(runner, temp_start_cli):
    """
    Test LOGON command: run saplogon application
    'sap logon'
    """
    # TODO: возможно нужно пробовать запускать окно и проверять, что оно вызвано. Вопрос как это сделать ?
    pass
