#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Helpers for testing """

from sap.api import Parameter, Sap_system
from pathlib import Path


def flat_actual(*systems):
    """ Removing unwanted elements from actual output as it was printed on screen """
    ret_sys = ''
    for system in systems:
        ret_sys += str(system).replace("\n", '').replace(' ', '')
        if len(systems) > 1:
            ret_sys += ','
    return ret_sys


def flat_expected(*systems):
    """ Removing unwanted elements from expected output as it was printed on screen """
    result = "("
    for system in systems:
        result += f'{str(system).replace(" ", "")},'

    if len(systems) > 1:
        result = result[:-1]  # removing last , if we have several systems
    result += ')'

    return result


def stub_print_parameters_list(*parameters: Parameter, title, color='', enum=False):
    """
    Print systems list without RICH.CONSOLE(RICH.TABLE) output
    """
    print(parameters)


def stub_print_system_list(*sap_systems: Sap_system, title, color='', verbose=False, timeout=0,
                           enum=False, command: str = '', command_type: str = '', url=False):
    """
    Print systems list without RICH.CONSOLE(RICH.TABLE) output
    """
    print(sap_systems)


def stub_print_message(message, message_type):
    """ Replace Rich's console.print(Panel) """
    print(message)


def stub_open_sap(arguments):
    """
    Stab function to replace utilities.open_sap
    """
    print(arguments)


def stub_launch(command_line_path, param):
    """  Substitute utilities.launch_command_line_with_params """
    print(f"{command_line_path} {param}")
