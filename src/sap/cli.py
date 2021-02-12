#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import click
import os
import subprocess
import time
import ctypes
import pyperclip
import sys
import sap.config
from contextlib import contextmanager
from sap.api import Sap_system
from sap.crypto import Crypto
import sap.utilities as utilities


@click.group()
def sap_cli():
    """ Скрипт для запуска SAP систем из командной строки """


# noinspection PyShadowingNames
@sap_cli.command('logon')
def logon():
    """ Запуск SAPLogon """

    # Считываем конфигурационный файл
    cfg = sap.config.Config()
    _config = cfg.read()

    saplogon_exe_path = _config.saplogon_path
    if not os.path.exists(saplogon_exe_path):
        click.echo(click.style(f'Путь до saplogon.exe не верный: \n{saplogon_exe_path} \n', bg='black', fg='yellow'))
        sys.exit()

    click.launch(saplogon_exe_path)


@sap_cli.command('pw')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
def pw(system, mandant):
    """ Копирует пароль от заданной системы в буфер обмена. Стирает буфер обмена через 15 секунд \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    with _sap_db():
        sap_system = Sap_system(str(system).upper(), str(mandant).upper() if mandant else '', '', '')
        result = sap.pw(sap_system)

        if not result:
            utilities.no_result_output(system, mandant)

        selected_system = choose_system([Sap_system(*item) for item in result])
        pyperclip.copy(Crypto.decrypto(selected_system.password))

        click.echo(click.style('Пароль скопирован в буфер обмена \n', bg='black', fg='green'))
        time.sleep(15)
        if ctypes.windll.user32.OpenClipboard(None):
            ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
        click.echo(click.style('Буфер обмена очищен \n', bg='black', fg='green'))
        click.pause('Нажмите для продолжения ...')


def choose_system(result, v=''):
    ans = 0
    if len(result) >= 2:
        utilities.print_system_list(result, 'Доступные системы', v=v)

        while int(ans) > len(result) or int(ans) < 1:
            if 1 <= int(ans) <= len(result):
                break
            click.echo(click.style(f"\nВозможно вводить значения только от 1 до {str(len(result))}.", bg='black',
                                   fg='white'))
            ans = click.prompt('Выберите систему, в которую хотите войти \n>>>', type=int)
        ans = ans - 1

    system = Sap_system(result[ans].system, result[ans].mandant, result[ans].user, result[ans].password)
    return system


# noinspection PyShadowingNames,PyUnboundLocalVariable,PyTypeChecker
@sap_cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', help='пользователь')
@click.option('-pw', help='пароль')
@click.option('-l', help='язык входа', default='RU')
@click.option('-v', help='показать параметры запуска', is_flag=True, type=click.BOOL)
@click.option('-t', help='код транзакции')
@click.option('-p', help='параметры для транзакции')
def run(system, mandant='', u='', pw='', l='RU', v=False, t='', p=''):
    """ Запуск указанной SAP системы \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    with _sap_db():
        sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3) if mandant else '',
                                str(u).upper() if u else '', '')
        result = sap.run(sap_system)

        if not result:
            utilities.no_result_output(str(system).upper(), str(mandant).zfill(3), u)

        cfg = sap.config.Config()
        _config = cfg.read()

        sapshcut_exe_path = _config.command_line_path
        if not os.path.exists(sapshcut_exe_path):
            click.echo(click.style('В INI файле не найден путь к sapshcut.exe \n', bg='black', fg='yellow'))
            click.pause('Нажмите для продолжения ...')
            sys.exit()

        selected_system = choose_system([Sap_system(*item) for item in result], v)

        if v:
            utilities.print_system_list([selected_system], 'Информация о запускаемой системе', v)
            click.pause('Нажмите для продолжения ... ')

        # Добавляем параметры для запуска SAP системы
        argument = [
            sapshcut_exe_path,  # Путь до sapshcut.exe
            f"-system={selected_system.system}",  # Id системы
            f"-client={str.zfill(selected_system.mandant, 3)}",  # Номер манданта
            f"-user={u}" if u else f"-user={selected_system.user}",  # Пользователь
            f"-pw={pw}" if pw else f"-pw={Crypto.decrypto(selected_system.password)}",  # Пароль
            f"-language={l}",  # Язык для входа
            '-maxgui',  # Развернуть окно на весь экран
        ]

        # Добавляем код транзакции
        if t:
            if p:
                # TODO: Доделать запуск транзакции с параметрами

                param_data = sap.query_param(str(t).upper())

                item = f"-command=\"*{t.upper()} {param_data[0][1]}={p}\""
                # item = '-command="*TM_52 VTGFHA-BUKRS=TRM1;"'  # VTGFHA-RFHA=100000000057;" '

                argument.append(item)
                print(item)
            else:
                item = '-command=' + t
                argument.append(item)
            item = '-type=transaction'
            argument.append(item)

        # Запускаем SAP
        ret = subprocess.call(argument)

        if ret:
            click.echo(ret)
            click.pause('Нажмите для продолжения ...')


@sap_cli.command('db')
def database():
    """ Создание базы данных для хранеия информкции о SAP системах """
    pass
    # db = Database()
    # db.create()


@sap_cli.command('add')
@click.option('-system', prompt=True, help='SAP system')
@click.option(
    '-mandant', prompt=True, help='SAP Client', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='SAP user')
@click.option(
    '-password',
    help='SAP password',
    prompt=True,
    # confirmation_prompt=True,
    # hide_input=True,
)
def add(system, mandant, user, password):
    """ Add sap system with it's parameters to db."""

    with _sap_db():
        encrypted_password = Crypto.encrypto(str.encode(password))
        sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper(), encrypted_password)
        result = sap.add(sap_system)

    if result:
        click.echo(click.style('Не удалось добавить системы в базу данных ... \n', bg='red', fg='white'))
        click.echo(result)
    else:
        utilities.print_system_list([sap_system], 'Добавлена следующая система: ')

    click.pause('Нажмите для продолжения ...')


@sap_cli.command('update')
@click.option('-system', prompt=True, help='система')
@click.option(
    '-mandant', prompt=True, help='мандант', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='пользователь')
@click.option(
    '-password',
    help='пароль',
    prompt=True,

    # TODO: убрать комментарии для пароля

    # confirmation_prompt=True,
    # hide_input=True
)
def update(system, mandant, user, password):
    """ Обновление пароля для SAP системы """
    encrypted_password = Crypto.encrypto(str.encode(password))
    sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper(), encrypted_password)

    with _sap_db():
        result = sap.update(sap_system)

        if result is None:
            utilities.no_result_output(str(system).upper(), str(mandant).zfill(3), str(user).upper())
        else:
            utilities.print_system_list([sap_system], 'Обновленная система', True)
            click.pause('Нажмите для продолжения ...')


@sap_cli.command('delete')
@click.option('-system', prompt=True, help='система')
@click.option(
    '-mandant', prompt=True, help='мандант', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='пользователь')
def delete(system, mandant, user):
    """ Удаление указанной SAP системы из базы данных """
    mandant = int(str(mandant).zfill(3))
    sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper(), '')

    with _sap_db():
        result = sap.delete(sap_system)

        if not result:
            utilities.no_result_output(system, mandant, user)
            exit()

        utilities.print_system_list([sap_system], 'Удалена следующая система')
        click.pause('Нажмите для продолжения ...')


@sap_cli.command('config')
def config():
    """ Создание конфигурационного ini файла """

    cfg = sap.config.Config()

    if cfg.exists():
        click.echo(click.style('Config уже существует \n', bg='black', fg='yellow'))
        click.pause('Нажмите для продолжения ...')
    else:
        cfg.create()


@sap_cli.command('list')
@click.option('-s', required=False, help='показать выбранную систему')
@click.option('-v', help='показать пароли', is_flag=True)
def list_systems(s, v):
    """ Информация о SAP системах находящихся в базе данных """

    with _sap_db():
        result = sap.list_systems(str(s).upper() if s else '')

        if not result:
            utilities.no_result_output(s)

        utilities.print_system_list([Sap_system(*item) for item in result], 'Список доступных систем', v)
        click.pause('Нажмите для продолжения ...')


@sap_cli.command('keys')
def keys():
    """ Создание ключей шифрования """

    Crypto().generate_keys()


@sap_cli.command('ver', help='Текущая версия SAP shortcut')
def shortcut_version():
    # Считываем конфигурационный файл
    cfg = sap.config.Config()
    _config = cfg.read()

    utilities.launch_command_line_with_params(_config.command_line_path, '-version')


@sap_cli.command('help', help='SAP GUI shortcut help')
def shortcut_help():
    # Считываем конфигурационный файл
    cfg = sap.config.Config()
    _config = cfg.read()

    utilities.launch_command_line_with_params(_config.command_line_path, '-help')


@sap_cli.command('start')
def start():
    # TODO: создать команду для начального формирования ключей, базы данных, конфига и прописи всех данных в конфиг
    pass


@contextmanager
def _sap_db():
    cfg = sap.config.Config()
    _config = cfg.read()
    sap.start_sap_db(_config.db_path, _config.db_type)
    yield
    sap.stop_sap_db()


if __name__ == '__main__':
    sys.excepthook = utilities.show_exception_and_exit
    sap_cli()
