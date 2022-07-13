#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Helpers for testing """

from sap.api import Parameter, Sap_system


def flat_actual(system):
    """ Removing unwanted elements from actual output as it was printed on screen """
    return str(system).replace("\n", '').replace(' ', '')


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


def stub_launch(url=''):
    """
    Stab function to replace 'click.launch' for launching websites
    """
    return 0 if url else 1


def stub_launch(command_line_path, param):
    """  Substitute utilities.launch_command_line_with_params """
    print(f"{command_line_path} {param}")
