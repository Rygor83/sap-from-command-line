#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Command Line Tests for transactions' parameters commands: paradd, parlist, pardel, parupdate """

from sap.cli import sap_cli


def test_paradd_cli(runner, temp_start_cli):
    """  Testing paradd: adding new transaction """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "paradd",
                                          "-t", "SE11",
                                          "-p", "RSRD1-VIMA_VAL"])
    assert result.output == ('\n\n'
                             '               \x1b[32m\x1b[40mAvailable transactions and parameters\x1b[0m                \n'
                             '┌───────────────────────────────────┬─────────────────────────────────────────┐\n'
                             '│ Transaction                       │ Parameters                              │\n'
                             '╞═══════════════════════════════════╪═════════════════════════════════════════╡\n'
                             '│ SE11                              │ RSRD1-VIMA_VAL                          │\n'
                             '└───────────────────────────────────┴─────────────────────────────────────────┘\n')


def test_parupdate_existing_transaction_cli(runner, temp_start_cli):
    """ Testing parupdate: updating existing transaction """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parupdate",
                                          "-t", "SE11",
                                          "-p", "RSRD1-TBMA_VAL"])
    assert result.output == ('\n\n'
                             '               \x1b[32m\x1b[40mAvailable transactions and parameters\x1b[0m                \n'
                             '┌──────────┬──────────────────────────────┬───────────────────────────────────┐\n'
                             '│ Id       │ Transaction                  │ Parameters                        │\n'
                             '╞══════════╪══════════════════════════════╪═══════════════════════════════════╡\n'
                             '│ 1        │ SE11                         │ RSRD1-VIMA_VAL                    │\n'
                             '└──────────┴──────────────────────────────┴───────────────────────────────────┘\n'
                             '\n\n'
                             '                  \x1b[32m\x1b[40mThe following system is UPDATED\x1b[0m                   \n'
                             '┌───────────────────────────────────┬─────────────────────────────────────────┐\n'
                             '│ Transaction                       │ Parameters                              │\n'
                             '╞═══════════════════════════════════╪═════════════════════════════════════════╡\n'
                             '│ SE11                              │ RSRD1-TBMA_VAL                          │\n'
                             '└───────────────────────────────────┴─────────────────────────────────────────┘\n')


def test_parupdate_no_existing_transaction_cli(runner, temp_start_cli):
    """ Testing parupdate: updating not existing transaction """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parupdate",
                                          "-t", "SE12",
                                          "-p", "RSRD1-TBMA_VAL"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────────────────────────────┬────────────────────────────────────┐\n'
                             '│ Transaction                            │ Parameters                         │\n'
                             '╞════════════════════════════════════════╪════════════════════════════════════╡\n'
                             '│ SE12                                   │                                    │\n'
                             '└────────────────────────────────────────┴────────────────────────────────────┘\n')


def test_parlist_existing_transaction_cli(runner, temp_start_cli):
    """ Testing parlist: listing existing transaction """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parlist"])
    assert result.output == ('\n\n'
                             '               \x1b[32m\x1b[40mAvailable transactions and parameters\x1b[0m                \n'
                             '┌───────────────────────────────────┬─────────────────────────────────────────┐\n'
                             '│ Transaction                       │ Parameters                              │\n'
                             '╞═══════════════════════════════════╪═════════════════════════════════════════╡\n'
                             '│ SE11                              │ RSRD1-TBMA_VAL                          │\n'
                             '└───────────────────────────────────┴─────────────────────────────────────────┘\n')


def test_parlist_enumerated_existing_transaction_cli(runner, temp_start_cli):
    """ Testing parlist: listing existing transaction with enumeration """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parlist", '-e'])
    assert result.output == ('\n\n'
                             '               \x1b[32m\x1b[40mAvailable transactions and parameters\x1b[0m                \n'
                             '┌──────────┬──────────────────────────────┬───────────────────────────────────┐\n'
                             '│ Id       │ Transaction                  │ Parameters                        │\n'
                             '╞══════════╪══════════════════════════════╪═══════════════════════════════════╡\n'
                             '│ 1        │ SE11                         │ RSRD1-TBMA_VAL                    │\n'
                             '└──────────┴──────────────────────────────┴───────────────────────────────────┘\n')


def test_parlist_existing_transaction_partial_name_cli(runner, temp_start_cli):
    """ Testing parlist: listing existing transaction with partial name """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parlist",
                                          "-t", "SE1"])
    assert result.output == ('\n\n'
                             '               \x1b[32m\x1b[40mAvailable transactions and parameters\x1b[0m                \n'
                             '┌───────────────────────────────────┬─────────────────────────────────────────┐\n'
                             '│ Transaction                       │ Parameters                              │\n'
                             '╞═══════════════════════════════════╪═════════════════════════════════════════╡\n'
                             '│ SE11                              │ RSRD1-TBMA_VAL                          │\n'
                             '└───────────────────────────────────┴─────────────────────────────────────────┘\n')


def test_parlist_no_existing_transaction_cli(runner, temp_start_cli):
    """ Testing parlist: listing not existing transaction """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "parlist",
                                          "-t", 'SE13'])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────────────────────────────┬────────────────────────────────────┐\n'
                             '│ Transaction                            │ Parameters                         │\n'
                             '╞════════════════════════════════════════╪════════════════════════════════════╡\n'
                             '│ SE13                                   │                                    │\n'
                             '└────────────────────────────────────────┴────────────────────────────────────┘\n')


def test_pardelete_existing_transaction_cli(runner, temp_start_cli):
    """ Testing pardel: deleting existing transaction """
    runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                 "paradd",
                                 "-t", "SE11",
                                 "-p", "RSRD1-VIMA_VAL"])
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "pardel",
                                          "-t", "se11",
                                          "-confirm"])
    assert result.output == ('\n\n'
                             '               \x1b[32m\x1b[40mAvailable transactions and parameters\x1b[0m                \n'
                             '┌──────────┬──────────────────────────────┬───────────────────────────────────┐\n'
                             '│ Id       │ Transaction                  │ Parameters                        │\n'
                             '╞══════════╪══════════════════════════════╪═══════════════════════════════════╡\n'
                             '│ 1        │ SE11                         │ RSRD1-TBMA_VAL                    │\n'
                             '└──────────┴──────────────────────────────┴───────────────────────────────────┘\n'
                             '\n\n'
                             '   \x1b[32m\x1b[40mTrying to DELETE the following transaction and its parameters\x1b[0m    \n'
                             '┌───────────────────────────────────┬─────────────────────────────────────────┐\n'
                             '│ Transaction                       │ Parameters                              │\n'
                             '╞═══════════════════════════════════╪═════════════════════════════════════════╡\n'
                             '│ SE11                              │ RSRD1-TBMA_VAL                          │\n'
                             '└───────────────────────────────────┴─────────────────────────────────────────┘\n'
                             '\n\n'
                             '          \x1b[32m\x1b[40mThe following parameter is DELETED from database\x1b[0m          \n'
                             '┌───────────────────────────────────┬─────────────────────────────────────────┐\n'
                             '│ Transaction                       │ Parameters                              │\n'
                             '╞═══════════════════════════════════╪═════════════════════════════════════════╡\n'
                             '│ SE11                              │ RSRD1-TBMA_VAL                          │\n'
                             '└───────────────────────────────────┴─────────────────────────────────────────┘\n')


def test_pardelete_no_transaction_exists_cli(runner, temp_start_cli):
    """ Testing pardel: deleting not existing transaction """
    result = runner.invoke(sap_cli, args=["--config_path", temp_start_cli,
                                          "pardel",
                                          "-t", "se11",
                                          "-confirm"])
    assert result.output == ('\n\n'
                             '             \x1b[33m\x1b[40mNOTHING FOUND according to search criteria\x1b[0m             \n'
                             '┌────────────────────────────────────────┬────────────────────────────────────┐\n'
                             '│ Transaction                            │ Parameters                         │\n'
                             '╞════════════════════════════════════════╪════════════════════════════════════╡\n'
                             '│ SE11                                   │                                    │\n'
                             '└────────────────────────────────────────┴────────────────────────────────────┘\n')
