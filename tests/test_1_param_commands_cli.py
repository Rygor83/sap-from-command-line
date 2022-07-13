#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Command Line Tests for transactions' parameters commands: paradd, parlist, pardel, parupdate """

from pytest_mock import mocker  # DO NOT DELETE IT

from conftest_utilities import flat_actual, flat_expected, stub_print_parameters_list
from sap.api import Parameter
from sap.cli import sap_cli
import sap.utilities

parameter_1 = Parameter(transaction='SE11', parameter='RSRD1-VIMA_VAL')
parameter_2 = Parameter(transaction='SM30', parameter='VIEWNAME')
parameter_1_updated = Parameter(transaction='SE11', parameter='RSRD1-VIMA_VAL')


def test_paradd_1_cli(runner, temp_start_cli, mocker):
    """
    Testing PARADD: adding new transaction
    'paradd -t transaction_code -p screen_field'
    """
    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "paradd",
                                          "-t", parameter_1.transaction,
                                          "-p", parameter_1.parameter])

    assert flat_actual(result.output) == flat_expected(parameter_1)


def test_paradd_2_cli(runner, temp_start_cli, mocker):
    """
    Testing PARADD: adding new transaction
    'paradd -t transaction_code -p screen_field'
    """

    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "paradd",
                                          "-t", parameter_2.transaction,
                                          "-p", parameter_2.parameter])
    assert flat_actual(result.output) == flat_expected(parameter_2)


def test_parupdate_existing_transaction_cli(runner, temp_start_cli, mocker):
    """
    Testing PARUPDATE: updating existing transaction
    'parupdate -t transaction_code -p new_screen_field'
    """

    parameter_updated = Parameter(transaction='SE11', parameter='RSRD1-VIMA_VAL')

    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parupdate",
                                          "-t", parameter_updated.transaction,
                                          "-p", parameter_updated.parameter])
    assert flat_actual(result.output) == f"{flat_expected(parameter_1)}{flat_expected(parameter_updated)}"


def test_parupdate_no_existing_transaction_cli(runner, temp_start_cli, mocker):
    """
    Testing PARUPDATE: updating not existing transaction
    'parupdate -t transaction_code -p new_screen_field'
    """

    transaction = 'SE12'
    parameter = "RSRD1-TBMA_VAL"
    non_existing_parameter = Parameter(transaction=transaction)

    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parupdate",
                                          "-t", transaction,
                                          "-p", parameter])

    assert flat_actual(result.output) == flat_expected(non_existing_parameter)


def test_parlist_all_existing_transaction_cli(runner, temp_start_cli, mocker):
    """
    Testing PARLIST: listing all existing transaction
    'parlist'
    """

    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parlist"])
    assert flat_actual(result.output) == flat_expected(*[parameter_1_updated, parameter_2])


def test_parlist_enumerated_all_existing_transaction_cli(runner, temp_start_cli, mocker):
    """
    Testing PARLIST: listing all existing transaction with enumeration
    'parlist'
    """

    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "parlist", '-e'])
    assert flat_actual(result.output) == flat_expected(*[parameter_1_updated, parameter_2])


def test_parlist_existing_transaction_partial_name_cli(runner, temp_start_cli, mocker):
    """
    Testing PARLIST: listing existing transaction with partial name
    'parlist -t transaction_code/partial_transaction_code'
    """
    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parlist",
                                          "-t", "SE1"])
    assert flat_actual(result.output) == flat_expected(parameter_1_updated)


def test_parlist_no_existing_transaction_cli(runner, temp_start_cli, mocker):
    """
    Testing PARLIST: listing not existing transaction
    'parlist -t non_existing_transaction_code'
    """

    non_existing_parameter = Parameter(transaction='SE13')
    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parlist",
                                          "-t", non_existing_parameter.transaction])
    assert flat_actual(result.output) == flat_expected(non_existing_parameter)


def test_pardelete_existing_transaction_cli(runner, temp_start_cli, mocker):
    """
    Testing PARDEL: deleting existing transaction
    'pardel -t transaction_code'
    """

    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "pardel",
                                          "-t", parameter_1.transaction,
                                          "-confirm"])
    assert flat_actual(
        result.output) == f"{flat_expected(parameter_1)}{flat_expected(parameter_1)}{flat_expected(parameter_1)}"


def test_pardelete_no_transaction_exists_cli(runner, temp_start_cli, mocker):
    """
    Testing PARDEL: deleting not existing transaction
    'pardel -t non_existing_transaction_code'
    """

    non_existing_parameter = Parameter(transaction='SE11')

    mocker.patch.object(sap.utilities, 'print_parameters_list', new=stub_print_parameters_list)
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli, "pardel",
                                          "-t", non_existing_parameter.transaction,
                                          "-confirm"])
    assert flat_actual(result.output) == flat_expected(non_existing_parameter)
