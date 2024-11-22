#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Command Line Tests for main commands: add, list, delete, update """
import time
from pathlib import Path
import click
import pyperclip
import psutil
import pytest
from pytest_mock import mocker  # do not delete it

from conftest_utilities import flat_actual, flat_expected, stub_print_system_list, stub_print_message, stub_open_sap
from conftest_utilities import stub_launch
from sap.api import DEBUG_FILE_NAME, CONFIG_NAME, PUBLIC_KEY_NAME, PRIVATE_KEY_NAME, DATABASE_NAME
from sap.cli import sap_cli
from sap import Sap_system
import sap.utilities

PASSWORD = '12345678'
UPDATED_PASSWORD = '1029384756'

sap_system_1 = sap.Sap_system(system='ZZZ',
                              client='999',
                              user='USER25',
                              password=PASSWORD,
                              language='EN',
                              customer='Roga & copyta',
                              description='Develop',
                              url='',
                              autotype='',
                              only_web='yes', )
sap_system_2 = sap.Sap_system(system='YYY',
                              client='998',
                              user='USER21',
                              password=PASSWORD,
                              language='EN',
                              customer='Vasya Pupkin',
                              description='Production',
                              url='www.vasyapupkin.by',
                              autotype='{USER}{TAB}{PASS}{ENTER}',
                              only_web='yes', )
sap_system_3 = sap.Sap_system(system='XXX',
                              client='100',
                              user='USER15',
                              password=PASSWORD,
                              language='EN',
                              customer='XYZ systems',
                              description='Test',
                              url='www.XYZsystems.by',
                              autotype='{USER}{TAB}{PASS}{ENTER}',
                              only_web='yes', )
sap_system_1_updated = sap.Sap_system(system='ZZZ',
                                      client='999',
                                      user='USER25',
                                      password=UPDATED_PASSWORD,
                                      language='EN',
                                      customer='Roga & copyta',
                                      description='Dev',
                                      url='',
                                      autotype='',
                                      only_web='no', )
sap_system_2_updated = sap.Sap_system(system='YYY',
                                      client='998',
                                      user='USER21',
                                      password=PASSWORD,
                                      language='EN',
                                      customer='Vasya Pupkin',
                                      description='Production',
                                      url='www.vasyapupkin.by',
                                      autotype='{USER}{TAB}{PASS}{ENTER}',
                                      only_web='no', )

non_existing_system = Sap_system(system='BBB',
                                 client='',
                                 user='',
                                 password='',
                                 language='',
                                 customer='',
                                 description='',
                                 url='',
                                 autotype='',
                                 only_web='')


def test_start_cli(temp_start_cli):
    """
    Test START command: 'start' command works in temp_start_cli fixture. All we need is to check if files are created
    'sap start'
    """
    assert Path(temp_start_cli / CONFIG_NAME).exists() and Path(temp_start_cli / PUBLIC_KEY_NAME).exists() and Path(
        temp_start_cli / PRIVATE_KEY_NAME).exists() and Path(temp_start_cli / DATABASE_NAME).exists()


def test_add_system_1(runner, temp_start_cli, mocker):
    """
    Test ADD command: new system 1, basic fields
    'sap add'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli,
                                 "add",
                                 "-system", sap_system_1.system,
                                 "-client", sap_system_1.client,
                                 "-user", sap_system_1.user,
                                 "-password", sap_system_1.password,
                                 "-language", sap_system_1.language,
                                 "-customer", sap_system_1.customer,
                                 "-description", sap_system_1.description,
                                 "-url", sap_system_1.url if sap_system_1.url else "",
                                 "-autotype", sap_system_1.autotype if sap_system_1.autotype else "",
                                 "-only_web", sap_system_1.only_web if sap_system_1.only_web else ""], )

    # TODO: Нужно делать запрос в базу данных - и сравнивать результаты, а не выводы в терминал

    assert flat_actual(result.output) == flat_expected(sap_system_1)


def test_add_system_2_with_url(runner, temp_start_cli, mocker):
    """
    Test ADD command: new system 2, basic fields + url, autotype
    'sap add'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli,
                                 "add",
                                 "-system", sap_system_2.system,
                                 "-client", sap_system_2.client,
                                 "-user", sap_system_2.user,
                                 "-password", sap_system_2.password,
                                 "-language", sap_system_2.language,
                                 "-customer", sap_system_2.customer,
                                 "-description", sap_system_2.description,
                                 "-url", sap_system_2.url if sap_system_2.url else "",
                                 "-autotype", sap_system_2.autotype if sap_system_2.autotype else "",
                                 "-only_web", sap_system_1.only_web if sap_system_1.only_web else ""])

    assert flat_actual(result.output) == flat_expected(sap_system_2)


def test_add_system_3_verbose(runner, temp_start_cli, mocker):
    """
    Test ADD command: new system 3, basic fields + url, autotype + show password
    'sap add -v'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli,
                                 "add",
                                 "-system", sap_system_3.system,
                                 "-client", sap_system_3.client,
                                 "-user", sap_system_3.user,
                                 "-password", sap_system_3.password,
                                 "-language", sap_system_3.language,
                                 "-customer", sap_system_3.customer,
                                 "-description", sap_system_3.description,
                                 "-url", sap_system_3.url if sap_system_3.url else "",
                                 "-autotype", sap_system_3.autotype if sap_system_3.autotype else "",
                                 "-only_web", sap_system_1.only_web if sap_system_1.only_web else "",
                                 "-v",
                                 "-time", "1"])

    assert flat_actual(result.output) == flat_expected(sap_system_3)


def test_add_system_1_no_config_exists(runner, tmp_path, mocker):  # , temp_start_cli, mocker):
    """
    Test ADD command: new system 1, basic fields
    'sap add'
    """

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli,
                           args=["--config_path", tmp_path,
                                 "add",
                                 "-system", sap_system_1.system,
                                 "-client", sap_system_1.client,
                                 "-user", sap_system_1.user,
                                 "-password", sap_system_1.password,
                                 "-language", sap_system_1.language,
                                 "-customer", sap_system_1.customer,
                                 "-description", sap_system_1.description,
                                 "-url", sap_system_1.url if sap_system_1.url else "",
                                 "-autotype", sap_system_1.autotype if sap_system_1.autotype else "",
                                 "-only_web", sap_system_1.only_web if sap_system_1.only_web else ""])

    assert result.output.replace('\n', '') == ('SAP_CONFIG.INI does not exist.. Check path: '
                                               f'{tmp_path / CONFIG_NAME} '
                                               "Either run 'sap start' or 'sap config -create' to create and edit "
                                               'configAborted.')


def test_add_system_1_no_database_exists(runner, tmp_path, mocker, config_tmp_path):  # , temp_start_cli, mocker):
    """
    Test ADD command: new system 1, basic fields
    'sap add'
    """

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli,
                           args=["--config_path", tmp_path,
                                 "add",
                                 "-system", sap_system_1.system,
                                 "-client", sap_system_1.client,
                                 "-user", sap_system_1.user,
                                 "-password", sap_system_1.password,
                                 "-language", sap_system_1.language,
                                 "-customer", sap_system_1.customer,
                                 "-description", sap_system_1.description,
                                 "-url", sap_system_1.url if sap_system_1.url else "",
                                 "-autotype", sap_system_1.autotype if sap_system_1.autotype else "",
                                 "-only_web", sap_system_1.only_web if sap_system_1.only_web else ""])

    assert result.output.replace('\n', '') == (
        'Database does not exist or there is no possibility for connection.. Check '
        'the following path: '
        f'{tmp_path / DATABASE_NAME}Aborted.')


def test_list_existing_systems_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list all available systems
    'sap list'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list"])
    assert flat_actual(result.output) == flat_expected(*[sap_system_1, sap_system_2, sap_system_3])


def test_list_existing_systems_show_passwords_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list all available systems and show passwords
    'sap list -v'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-v", "-time", "1"])
    assert flat_actual(result.output) == flat_expected(*[sap_system_1, sap_system_2, sap_system_3])


def test_list_existing_system_with_system_client_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific system and client
    'sap list system_id client'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "list", sap_system_1.system, sap_system_1.client])
    assert flat_actual(result.output) == flat_expected(sap_system_1)


def test_list_existing_system_with_system_only_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific system only
    'sap list system_id'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", sap_system_1.system])
    assert flat_actual(result.output) == flat_expected(sap_system_1)


def test_list_existing_system_with_client_only_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific client
    'sap list % client'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "%", sap_system_1.client])
    assert flat_actual(result.output) == flat_expected(sap_system_1)


def test_list_existing_system_with_only_partial_client_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific partial client
    'sap list % client'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "%", "99"])
    assert flat_actual(result.output) == flat_expected(*[sap_system_1, sap_system_2])


def test_list_existing_system_with_customer_name_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific customer name
    'sap list -c customer_name'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-c", "roga"])
    assert flat_actual(result.output) == flat_expected(sap_system_1)


def test_list_existing_system_with_partial_customer_name_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific partial customer name
    'sap list -c customer_name'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-c", "va%in"])
    assert flat_actual(result.output) == flat_expected(sap_system_2)


def test_list_existing_system_with_user_name_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific username
    'sap list -u username'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-u", sap_system_2.user])
    assert flat_actual(result.output) == flat_expected(sap_system_2)


def test_list_existing_system_with_partial_user_name_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific partial username
    'sap list -u username'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-u", "user2"])
    assert flat_actual(result.output) == flat_expected(*[sap_system_1, sap_system_2])


def test_list_existing_system_with_system_description_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific system description
    'sap list -d system_description'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "-d", sap_system_1.description])
    assert flat_actual(result.output) == flat_expected(sap_system_1)


def test_list_existing_system_with_url_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list system with specific system and show url, autotype information
    'sap list system_id -url'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", sap_system_2.system, "-u"])
    assert flat_actual(result.output) == flat_expected(sap_system_2)


def test_list_existing_systems_enumerated_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: list enumerated all systems
    'sap list --enum'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", "--enum"])
    assert flat_actual(result.output) == flat_expected(*[sap_system_1, sap_system_2, sap_system_3])


def test_list_no_existing_systems_cli(runner, temp_start_cli, mocker):
    """
    Test LIST command: Request for a non-existent system
    'sap list non_existent_system_id'
    """

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "list", non_existing_system.system])
    assert flat_actual(result.output) == flat_expected(non_existing_system)


def test_pw_no_clipboard_clear_cli(runner, temp_start_cli):
    """
    Test PW command: copying password into clipboard. For this test we do not clear clipboard.
    'sap pw system_id'
    """
    runner.invoke(sap_cli,
                  args=["--config_path", temp_start_cli,
                        "copy", "password", "zzz", "--no_clear"])
    password_from_database = pyperclip.paste()

    assert password_from_database == PASSWORD


def test_pw_clipboard_clear_cli(runner, temp_start_cli, mocker):
    """
    Test PW command: copying password into clipboard. And clear clipboard.
    'sap pw system_id'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    mocker.patch.object(sap.utilities, 'print_message', return_value=True)
    mocker.patch.object(sap.utilities, 'countdown', return_value=True)

    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "copy", "password", sap_system_3.system, "--clear",
                                 "-time",
                                 "1"])
    assert flat_actual(result.output) == flat_expected(sap_system_3)


def test_pw_no_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test PW command: Request for a non-existent system to get password
    'sap pw non_existent_system_id'
    """

    non_existing_system = 'BBB'
    sap_system_bbb = Sap_system(non_existing_system, client='', user='', password='', language='', customer='',
                                description='', url='', autotype='', only_web='')

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    mocker.patch.object(sap.utilities, 'print_message', return_value=True)
    mocker.patch.object(sap.utilities, 'countdown', return_value=True)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "copy", "password", non_existing_system])
    assert flat_actual(result.output) == flat_expected(sap_system_bbb)


def test_run_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", sap_system_2.system])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -reuse=1')


def test_run_existing_system_with_user_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", "-u", sap_system_2.user])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -reuse=1')


def test_run_existing_system_new_window_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    'sap run system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-n"])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -reuse=0')


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
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-l", language])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language={language} -maxgui -reuse=1')


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
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-eu"],
                           input=f"{external_user}\n{external_password}\n")
    assert str(result.output).replace("\n", "") == (
        f'Enter external user id: Warning: Password input may be echoed.Enter password for external user: "path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={external_user} -pw={external_password} -language=RU -maxgui -reuse=1')


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
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-t", transaction_code])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -type=transaction -command={transaction_code} -reuse=1')


def test_run_existing_system_with_transaction_and_parameter_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: request specific system
    Best way to test it is to check command line from argument variable
    !!!! PARAMETER INFO FOR TRANSACTION IS TAKEN FROM PARAMETERS TESTS !!!! Run both test_1* and test_2*
    'sap run system_id'
    """
    transaction_code = 'SM30'
    view_name = 'V_T001'

    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)  # do not open sap, but print command parameters
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-t",
                                 transaction_code, "-p", view_name])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -type=transaction -command="*{transaction_code} VIEWNAME={view_name};" -reuse=1')


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
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system,
                                 "-t", transaction_code, "-p", view_name])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -type=transaction -command="*{transaction_code} VIEWNAME={view_name};" -reuse=1')


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
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-s", system_command])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -type=SystemCommand -command={system_command} -reuse=1')


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
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-r", report_name])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -type=report -command={report_name} -reuse=1')


def test_run_web_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: Request for a non-existent system's web version
    'sap run system_id -w'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    mocker.patch.object(sap.utilities, 'print_message', return_value=True)
    mocker.patch.object(sap.utilities, 'open_url', return_value=True)
    mocker.patch.object(sap.utilities, 'launch_autotype_sequence', return_value=True)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "run", sap_system_2.system, "-w", "-time", '1'])
    assert flat_actual(result.output) == flat_expected(sap_system_2)


def test_run_web_existing_system_without_url_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: Request for a non-existent system's web version
    'sap run system_id -w'
    """
    sap_system_1_temp = Sap_system(sap_system_1.system)

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    mocker.patch.object(sap.utilities, 'print_message', return_value=True)
    mocker.patch.object(click, 'launch', return_value="")
    mocker.patch.object(sap.utilities, 'launch_autotype_sequence', return_value=True)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", sap_system_1.system, "-w"])

    assert flat_actual(result.output) == f"{flat_expected(sap_system_1)}{flat_expected(sap_system_1_temp)}Aborted."


def test_run_web_no_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test RUN command: Request for a non-existent system's web version
    'sap run system_id -w'
    """
    non_existing_sap_system = Sap_system(system='BBB', client='', user='', password='', customer='', description='',
                                         url='', autotype='')

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    mocker.patch.object(sap.utilities, 'print_message', return_value=True)
    mocker.patch.object(click, 'launch', return_value="")
    mocker.patch.object(sap.utilities, 'launch_autotype_sequence', return_value=True)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "run", non_existing_sap_system.system, "-w"])
    assert flat_actual(result.output) == flat_expected(non_existing_sap_system)


def test_debug_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test DEBUG command
    'sap debug system_id'
    """
    mocker.patch.object(sap.utilities, 'check_if_path_exists', return_value=True)
    mocker.patch.object(sap.utilities, 'print_system_list', return_value=True)
    mocker.patch.object(sap.utilities, 'open_sap', new=stub_open_sap)
    result = runner.invoke(sap_cli,
                           args=["--config_path", temp_start_cli, "debug", sap_system_2.system])
    assert str(result.output).replace("\n", "") == (
        f'"path to sapshcut.exe file." -system={sap_system_2.system} -client={sap_system_2.client} -user={sap_system_2.user} -pw={sap_system_2.password} -language=RU -maxgui -reuse=1 -command=/H -type=SystemCommand')


def test_debug_no_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test DEBUG command: Request for a non-existent system to delete
    'sap debug non_existent_system_id'
    """

    non_existing_sap_system = Sap_system(system='BBB', client='', user='', password='', customer='', description='',
                                         url='', autotype='')

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "debug", non_existing_sap_system.system])
    assert flat_actual(result.output) == flat_expected(non_existing_sap_system)


def test_debug_file_not_open(runner, temp_start_cli):
    """
    Test DEBUG command: create debug file
    'sap debug -f -not_open'
    """
    runner.invoke(sap_cli, args=["-path", temp_start_cli, 'debug', '-f', '-not_open'])
    debug_file = temp_start_cli / DEBUG_FILE_NAME
    with debug_file.open(encoding='utf-8') as file:
        text = file.read()
    assert text == '[FUNCTION]\nCommand =/H\nTitle=Debugger\nType=SystemCommand'


def test_logon_cli(runner, temp_start_cli, mocker):
    """
    Test LOGON command: run saplogon application. For this all we need is to check if application exists.
    click.launch will launch any exe file if it exists.
    'sap logon'
    """

    def check_if_process_running(process_name):
        for process in psutil.process_iter(['name']):
            if process.info['name'] == process_name:
                return True
        return False

    path_to_saplogon = Path("c:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe")
    # mocker.patch.object(click, 'launch', return_value=True)
    result = runner.invoke(sap_cli, args=["logon", "-s", path_to_saplogon])
    time.sleep(5)
    assert check_if_process_running("saplogon.exe") == True


def test_logon_wrong_saplogon_path_cli(runner, temp_start_cli, mocker):
    """
    Test LOGON command: run saplogon application
    'sap logon'
    """

    mocker.patch.object(sap.utilities, 'print_message', new=stub_print_message)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "logon"])
    assert str(result.output).replace('\n', '') == (
        'Executable does not exist: path to saplogon.exe file. Check the '
        'following path: path to saplogon.exe file.Aborted.')


def test_update_requesting_system_client_cli(runner, temp_start_cli, mocker):
    """
    Test UPDATE command: updating specific system
    'sap update system_id client'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["-path", temp_start_cli, "update", "zzz", "999"],
                           input=f"{sap_system_1_updated.password}\n\n{sap_system_1_updated.description}\n\n\n")

    expected_results = flat_expected(sap_system_1)
    expected_results += flat_actual(f''' 
            Enter new password [12345678]: {sap_system_1_updated.password}\n
            Enter Customer [Roga & copyta]: \n
            Enter system description [Develop]: {sap_system_1_updated.description}\n
            Enter URL []: \n
            Enter Autotype sequence []: \n''')
    expected_results += flat_expected(sap_system_1_updated)

    assert flat_actual(result.output) == expected_results


def test_update_choosing_system_from_list_cli(runner, temp_start_cli, mocker):
    """
    Test UPDATE command: choosing system from list to update it
    'sap update'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli,
                           args=["-path", temp_start_cli,
                                 "update"],
                           input=f"2\n\n\n{sap_system_2_updated.description}\n\n\n")

    expected_results = flat_expected(*[sap_system_1_updated, sap_system_2, sap_system_3])
    expected_results += flat_actual(f""" 
            Choose a system you want to login. Available values from 1 to 3: \n
            >>>: \n
            Enter new password [12345678]: \n
            Enter Customer [Vasya Pupkin]: \n
            Enter system description [Production]: {sap_system_2_updated.description}\n
            Enter URL [www.vasyapupkin.by]: \n
            Enter Autotype sequence""" + "[{USERNAME}{TAB}{PASSWORD}{ENTER}]: \n")
    expected_results += flat_expected(sap_system_2_updated)

    assert flat_actual(result.output) == expected_results


def test_update_no_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test UPDATE command: Request for a non-existent system to update
    'sap update non_existent_system_id'
    """

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "update", non_existing_system.system])
    assert flat_actual(result.output) == flat_expected(non_existing_system)


def test_delete_existing_system_choosing_from_list_cli(runner, temp_start_cli, mocker):
    """
    Test DELETE command: choosing system from list to delete it
    'sap delete'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "delete"], input="3\ny\n")

    expected_results = flat_actual(*[sap_system_1_updated, sap_system_2_updated, sap_system_3])
    expected_results = expected_results[:-1] + ')'
    expected_results += flat_actual(f""" 
                Choose a system you want to login. Available values from 1 to 3: \n
                >>>: \n\n""")
    expected_results += flat_expected(sap_system_3)
    expected_results += flat_actual(f"Do you really want to delete the system? [y/N]: y\n")
    expected_results += flat_expected(sap_system_3)[:-2]

    assert flat_actual(result.output) == flat_expected(expected_results)


def test_delete_existing_system_by_system_id_cli(runner, temp_start_cli, mocker):
    """
    Test DELETE command: choosing system by system id to delete it
    'sap delete system_id'
    """
    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "delete", "zzz"], input="y\n")

    expected_results = flat_actual(sap_system_1_updated) + ',)('
    expected_results += flat_actual(sap_system_1_updated) + ',)'
    expected_results += flat_actual(f"Do you really want to delete the system? [y/N]: y\n")
    expected_results += flat_expected(sap_system_1_updated)[:-2]

    assert flat_actual(result.output) == flat_expected(expected_results)


def test_delete_no_existing_system_cli(runner, temp_start_cli, mocker):
    """
    Test DELETE command: Request for a non-existent system to delete
    'sap delete non_existent_system_id'
    """

    mocker.patch.object(sap.utilities, 'print_system_list', new=stub_print_system_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "delete", non_existing_system.system])
    assert flat_actual(result.output) == flat_expected(non_existing_system)


def test_shortcut(runner, temp_start_cli, mocker):
    """
    Test SHORTCUT command: testing parameters to launch
    'sap shortcut'
    """
    mocker.patch.object(sap.utilities, 'launch_command_line_with_params', new=stub_launch)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "shortcut"])
    assert str(result.output).strip() == "path to sapshcut.exe file. -help"


def test_about(runner, temp_start_cli, mocker):
    """
    Test ABOUT command: testing parameters to launch
    'sap about'
    """
    mocker.patch.object(sap.utilities, 'launch_command_line_with_params', new=stub_launch)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "about"])
    assert str(result.output).strip() == "path to sapshcut.exe file. -version"


def test_keys_already_created(runner, temp_start_cli, mocker):
    """ Test KEYS command """

    # TODO: https://rich.readthedocs.io/en/stable/console.html

    mocker.patch.object(sap.utilities, 'print_message', stub_print_message)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "keys"])
    assert result.output == f"""\nEncryption keys already exist: \nPrivate: {temp_start_cli / PRIVATE_KEY_NAME}\nPublic: {temp_start_cli / PUBLIC_KEY_NAME}\nAborted.\n"""
