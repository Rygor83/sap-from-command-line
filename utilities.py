#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import traceback

from prettytable import PrettyTable

from crypto import *


def show_exception_and_exit(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb)
    click.pause('Нажмите для продолжения ...')
    sys.exit(-1)


def print_sys_table(systems: list, v: bool = 0):
    # TODO: Сделать функцию динамическую, чтобы можно было засовывать разные заголовки

    header = ['№', 'Система', 'Мандант', 'Пользователь']
    if v:
        header.append('Пароль')
    t = PrettyTable(header)
    for count, system in enumerate(systems, start=1):
        row = [count, system[0], system[1], system[2]]
        if v:
            row.append(Crypto.decrypto(system[3]))
        t.add_row(row)
    click.echo(t)


# noinspection PyDefaultArgument
def print_log(messages=[], systems=[], v: bool = 0, stop=''):
    click.echo()
    for message in messages:
        click.echo(message)
    if systems:
        print_sys_table(systems, v)
    if stop == 'X':
        click.echo()
        return click.pause('Нажмите для продолжения ...')
    elif stop == 'Y':
        ans = input('> ')
        return ans
    elif stop == 'Z':
        return
    else:
        click.echo()
        return click.pause('нажмите Enter ...')
