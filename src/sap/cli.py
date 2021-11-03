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
import time

import sap.config
from contextlib import contextmanager
from sap.api import Sap_system
from sap.crypto import Crypto
import sap.utilities as utilities


@click.group()
def sap_cli():
    """ Скрипт для запуска SAP систем из командной строки """


@sap_cli.command('logon')
def logon():
    """ Запуск SAPLogon """

    cfg = sap.config.Config()
    _config = cfg.read()

    saplogon_exe_path = _config.saplogon_path
    if not os.path.exists(saplogon_exe_path):
        click.echo(click.style(f'Путь до saplogon.exe не верный: \n{saplogon_exe_path} \n', **utilities.color_warning))
        sys.exit()

    click.launch(saplogon_exe_path)


@sap_cli.command('pw')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
def pw(system, mandant):
    """ Копирует пароль от заданной системы в буфер обмена. Стирает буфер обмена через 15 секунд \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    with _sap_db():
        timeout = 15

        sap_system = Sap_system(str(system).upper(), str(mandant).upper() if mandant else '')
        result = sap.pw(sap_system)

        if not result:
            # utilities.no_result_output(system, mandant)
            utilities.print_system_list([Sap_system(str(system).upper(), mandant)],
                                        'По следующим параметрам ничего не найдено', utilities.header_nsm)
        else:
            selected_system = utilities.choose_system(
                [Sap_system(item[0], item[1], item[2], Crypto.decrypto(item[3])) for item in result])
            pyperclip.copy(selected_system.password)

            click.echo(
                click.style(f'Пароль скопирован в буфер обмена.\nБуфер обмена будет очищен через {timeout} секунд.\n',
                            **utilities.color_message))
            click.echo(
                click.style(
                    'Если пользуетесь Clipboard manager, то следует внести приложения PY.EXE, CMD.EXE в исключения,\n'
                    'чтобы не хранить чувствительну информацию.\n',
                    **utilities.color_sensitive))

            time.sleep(timeout)
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()

            click.echo(click.style('Буфер обмена очищен. \n', **utilities.color_message))


@sap_cli.command('debug')
@click.argument('system', required=False)
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', '--user', 'user', help='пользователь')
@click.option('-pw', '--password', 'password', help='пароль')
@click.option('-l', '--language', 'language', help='язык входа', default='RU')
@click.option('-f', '--file', 'file', help='создать файл для печати', is_flag=True, type=click.BOOL)
def debug(system, mandant='', user='', password='', language='RU', file=False):
    ''' Запуск дебага любой выбранной системы или создание файла для дебага диалоговых окон'''

    if file:
        file_name = 'DEBUG.TXT'

        click.echo(f'Сейчас создастся файл {file_name}')
        click.echo('Сразу после создания откроется папка с файлом\n')
        click.pause('Нажмите любую клавишу')

        path = utilities.path()
        file_path = path + '\\' + file_name
        with open(file_path, 'w') as writer:
            writer.write('[FUNCTION]\n')
            writer.write('Command =/H\n')
            writer.write('Title=Debugger\n')
            writer.write('Type=SystemCommand')

        raw_s = r'explorer /select,' + r'{}'.format(file_path)
        subprocess.Popen(raw_s)

    else:
        with _sap_db():
            sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3) if mandant else '',
                                    str(user).upper() if user else '')
            result = sap.run(sap_system)

            if not result:
                utilities.no_result_output(str(system).upper(), str(mandant).zfill(3), user)

            cfg = sap.config.Config()
            _config = cfg.read()

            sapshcut_exe_path = _config.command_line_path
            if not os.path.exists(sapshcut_exe_path):
                click.echo(click.style('В INI файле не найден путь к sapshcut.exe \n', **utilities.color_warning))
                sys.exit()

            selected_system = utilities.choose_system(
                [Sap_system(item[0], item[1], item[2], Crypto.decrypto(item[3]), '', item[4], item[5]) for item in
                 result])

            # Добавляем параметры для запуска SAP системы
            argument = [
                sapshcut_exe_path,  # Путь до sapshcut.exe
                f"-system={selected_system.system}",  # Id системы
                f"-client={str.zfill(selected_system.mandant, 3)}",  # Номер манданта
                f"-user={user}" if user else f"-user={selected_system.user}",  # Пользователь
                f"-pw={password}" if password else f"-pw={selected_system.password}",  # Пароль
                f"-language={language}",  # Язык для входа
                '-maxgui',  # Развернуть окно на весь экран
            ]

            item = '-command=/H'
            argument.append(item)
            item = '-type=SystemCommand'
            argument.append(item)

            ret = subprocess.call(argument)


@sap_cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', '--user', 'user', help='пользователь')
@click.option('-pw', '--password', 'password', help='пароль')
@click.option('-l', '--language', 'language', help='язык входа', default='RU')
@click.option('-t', '--transaction', 'transaction', help='код транзакции')
@click.option('-p', '--parameter', 'parameter', help='параметры для транзакции')
def run(system, mandant='', user='', password='', language='RU', transaction='', parameter=''):
    """ Запуск указанной SAP системы \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    with _sap_db():
        sap_system = Sap_system(str(system).upper(),
                                str(mandant).zfill(3) if mandant else '',
                                str(user).upper() if user else '', '', '', '', '')
        result = sap.run(sap_system)

        if not result:
            utilities.no_result_output(str(system).upper(), str(mandant).zfill(3), user)

        cfg = sap.config.Config()
        _config = cfg.read()

        sapshcut_exe_path = _config.command_line_path
        if not os.path.exists(sapshcut_exe_path):
            click.echo(click.style('В INI файле не найден путь к sapshcut.exe \n', **utilities.color_warning))
            sys.exit()

        selected_system = utilities.choose_system(
            [Sap_system(item[0], item[1], item[2], Crypto.decrypto(item[3]), '', item[4], item[5]) for item in result])

        # Добавляем параметры для запуска SAP системы
        argument = [
            sapshcut_exe_path,  # Путь до sapshcut.exe
            f"-system={selected_system.system}",  # Id системы
            f"-client={str.zfill(selected_system.mandant, 3)}",  # Номер манданта
            f"-user={user}" if user else f"-user={selected_system.user}",  # Пользователь
            f"-pw={password}" if password else f"-pw={selected_system.password}",  # Пароль
            f"-language={language}",  # Язык для входа
            '-maxgui',  # Развернуть окно на весь экран
        ]

        if transaction:
            item = '-type=transaction'
            argument.append(item)

            if parameter:
                # TODO: Доделать запуск транзакции с параметрами

                # param_data = sap.query_param(str(transaction).upper())

                # item = f"-command=\"*{transaction.upper()} {param_data[0][1]}={parameter}\""
                # item = '-command=\"*TM_52 VTGFHA-BUKRS=TRM1; VTGFHA-RFHA=100000000057;\"'
                item = '-command=\"/n*FBM1 BKPF-BUKRS=1000;\"'
                argument.append(item)

                print(item)
            else:
                item = '-command=' + transaction
                argument.append(item)

        # Показываем, что будем запускать
        if transaction:
            header = utilities.header_nsmut
        else:
            header = utilities.header_nsmu

        # TODO: Доработать вывод

        utilities.print_system_list([Sap_system(selected_system.system,
                                                selected_system.mandant,
                                                selected_system.user,
                                                '',
                                                str(transaction).upper() if transaction else '',
                                                selected_system.customer,
                                                selected_system.description)],
                                    'Пробуем запустить следующую систему',
                                    header)

        # Запускаем SAP
        ret = subprocess.call(argument)

        if ret:
            click.echo(ret)


@sap_cli.command('db')
def database():
    """ Создание базы данных для хранеия информкции о SAP системах """
    pass
    # db = Database()
    # db.create()


@sap_cli.command('add')
@click.option('-system', prompt=True, help='SAP system')
@click.option('-mandant', prompt=True, help='SAP Client', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='SAP user')
@click.option('-password', help='SAP password', prompt=True, confirmation_prompt=True,
              # hide_input=True,
              )
@click.option('-customer', prompt=True, help="Customer", type=click.STRING)
@click.option('-description', prompt=True, help="System description", type=click.STRING)
def add(system, mandant, user, password, description, customer):
    """ Add sap system with it's parameters to db."""

    with _sap_db():
        encrypted_password = Crypto.encrypto(str.encode(password))
        sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper(), encrypted_password,
                                '', str(customer).upper(), str(description))
        result = sap.add(sap_system)

    if result:
        click.echo(click.style('Не удалось добавить системы в базу данных ... \n', **utilities.color_sensitive))
        click.echo(result)
    else:
        utilities.print_system_list([sap_system], 'Добавлена следующая система: ', utilities.header_nsmu)


@sap_cli.command('update')
@click.option('-system', prompt=True, help='система')
@click.option(
    '-mandant', prompt=True, help='мандант', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='пользователь')
@click.option(
    '-password',
    help='пароль',
    prompt=True,
    confirmation_prompt=True,
    # hide_input=True
)
@click.option('-customer', prompt=True, help="Customer", type=click.STRING)
@click.option('-description', prompt=True, help="System description", type=click.STRING)
def update(system, mandant, user, password, customer, description):
    """ Обновление пароля для SAP системы """

    # TODO: вставлять данные уже сущетсвующей системы, чтобы пользователь мог
    #  решить, изменять или не изменять.

    encrypted_password = Crypto.encrypto(str.encode(password))
    sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper(), password, '', str(customer),
                            str(description))
    sap_encrypted_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper(), encrypted_password,
                                      '', str(customer), str(description))

    with _sap_db():
        result = sap.update(sap_encrypted_system)

        if result is None:
            utilities.print_system_list([sap_system], 'Обновленная система', utilities.header_nsmu, verbose=True)
            click.pause('Нажмите для продолжения. Данные с паролем будут очищены с экрана ...')
            os.system('cls')
        else:
            utilities.no_result_output(str(system).upper(), str(mandant).zfill(3), str(user).upper())


@sap_cli.command('delete')
@click.option('-system', prompt=True, help='система')
@click.option(
    '-mandant', prompt=True, help='мандант', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='пользователь')
def delete(system, mandant, user):
    """ Удаление указанной SAP системы из базы данных """
    mandant = int(str(mandant).zfill(3))
    sap_system = Sap_system(str(system).upper(), str(mandant).zfill(3), str(user).upper(), '', '', '', '')

    with _sap_db():
        result = sap.delete(sap_system)

        if not result:
            utilities.no_result_output(system, mandant, user)
            exit()

        utilities.print_system_list([sap_system], 'Удалена следующая система', utilities.header_nsmu)


@sap_cli.command('config')
def config():
    """ Создание конфигурационного ini файла """

    cfg = sap.config.Config()

    if cfg.exists():
        click.echo(click.style('Config уже существует \n', **utilities.color_warning))
        click.echo(utilities.path())
    else:
        cfg.create()


@sap_cli.command('list')
@click.option('-s', '--system', 'system', required=False, help='показать выбранную систему')
@click.option('-v', '--verbose', 'verbose', help='показать пароли', is_flag=True)
def list_systems(system, verbose):
    """ Информация о SAP системах находящихся в базе данных """

    with _sap_db():
        result = sap.list_systems(str(system).upper() if system else '')

        if not result:
            utilities.no_result_output(system)

        systems_list = [
            Sap_system(item[0], item[1], item[2], Crypto.decrypto(item[3]) if verbose else '', '', item[4], item[5]) for
            item in result]

        utilities.print_system_list(systems_list, 'Список доступных систем', utilities.header_nsmu, verbose)
        if verbose:
            click.pause('Нажмите для продолжения. Данные о паролях будут очищены с экрана ...')
            os.system('cls')
        else:
            pass


@sap_cli.command('keys')
def keys():
    """ Создание ключей шифрования """

    Crypto().generate_keys()


@sap_cli.command('ver', help='Текущая версия SAP shortcut')
def shortcut_version():
    # Считываем конфигурационный файл
    cfg = sap.config.Config()
    _config = cfg.read()

    parameter = '-version'
    utilities.launch_command_line_with_params(_config.command_line_path, parameter)


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


@sap_cli.command('backup')
def backup():
    # TODO: создать команду для бэкапа ini фалов, sap logon систем
    # Бэкап должен шифроваться текущим ключом шифрования

    # Пути к saplogon.ini брать отсюда 2580439
    pass


@sap_cli.command('launch')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', '--user', 'user', help='пользователь')
@click.option('-pw', '--password', 'password', help='пароль')
@click.option('-l', '--language', 'language', help='язык входа', default='RU')
@click.option('-t', '--transaction', 'transaction', help='код транзакции')
@click.option('-p', '--parameter', 'parameter', help='параметры для транзакции')
def launch(system, mandant='', user='', password='', language='RU', transaction='', parameter=''):
    """ Launch sap system in web """

    # TODO: сделать таблицу https ардесов для SAP системы,
    # путь до браузера, чтобы запускать их в браузере.
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
