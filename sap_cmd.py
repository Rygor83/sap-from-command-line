#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import subprocess
import time
import ctypes
import pyperclip

from database import *
from utilities import *
from config import *

msg = []
sys_list = []


@click.group()
def cli():
    """ Скрипт для запуска SAP систем из командной строки """


# noinspection PyShadowingNames
@cli.command('logon')
def logon():
    """ Запуск SAPLogon """

    # Считываем конфигурационный файл
    config = Config()
    config.read()

    # Запускаем saplogon.exe
    saplogon_exe_path = config.data['APPLICATION']['sap']
    if not str(saplogon_exe_path).endswith('saplogon.exe'):
        click.echo(click.style('В ini файле не найден путь к saplogon.exe \n', bg='black', fg='yellow'))
        click.pause('Нажмите для продолжения ...')
        sys.exit()

    click.launch(saplogon_exe_path)


@cli.command('pw')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
def pw(system, mandant):
    """ Копирует пароль от заданной системы в буфер обмена. Стирает буфер обмена через 15 секунд \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    db = Database()
    sap_data = db.query(str(system).upper(), mandant)

    ans = ''
    if len(sap_data) >= 2:
        msg.clear()
        msg.append('Выбраны следующие пользователи: ')
        print_log(msg, sap_data, stop='Z')

        while not ans.isdigit() or int(ans) > len(sap_data) or int(ans) < 1:
            if ans.isdigit() and 1 <= int(ans) <= len(sap_data):
                break
            msg.clear()
            msg.append(f"Возможно вводить значения только от 1 до {str(len(sap_data))}.")
            msg.append('Выберите пользователя, под которым хотим войти в систему')
            ans = print_log(msg, stop='Y')
        ans = int(ans) - 1
    else:
        ans = 0

    pyperclip.copy(Crypto.decrypto(sap_data[ans][3]))
    msg.clear()
    msg.append('Пароль скопирован в буфер обмена')
    ans = print_log(msg, stop='Z')
    time.sleep(15)
    if ctypes.windll.user32.OpenClipboard(None):
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
    msg.clear()
    msg.append('Буфер обмена очищен')
    ans = print_log(msg, stop='X')


# noinspection PyShadowingNames,PyUnboundLocalVariable,PyTypeChecker
@cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', help='пользователь')
@click.option('-pw', help='пароль')
@click.option('-l', help='язык входа', default='RU')
@click.option('-v', help='показать параметры запуска', is_flag=True, type=click.BOOL)
@click.option('-t', help='код транзакции')
@click.option('-p', help='параметры для транзакции')
def run(system, mandant, u='', pw='', l='RU', v=0, t='', p=''):
    """ Запуск указанной SAP системы \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    # Считываем конфигурационный файл
    config = Config()
    config.read()

    sapshcut_exe_path = config.data['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('sapshcut.exe'):
        click.echo(click.style('В INI файле не найден путь к sapshcut.exe \n', bg='black', fg='yellow'))
        click.pause('Нажмите для продолжения ...')
        sys.exit()

    # Подсоединяемся к базе данных и запрашиваем данные
    msg.append(f"Пробуем запустить {str(system).upper()} {mandant if mandant else ''} {t.upper() if t else ''}")
    print_log(msg, stop='Z')

    db = Database()
    sap_data = db.query(str(system).upper(), mandant, str(u).upper() if u else '')

    ans = ''
    if len(sap_data) >= 2:
        msg.clear()
        msg.append('Выбраны следующие пользователи: ')
        print_log(msg, sap_data, stop='Z')

        while not ans.isdigit() or int(ans) > len(sap_data) or int(ans) < 1:
            if ans.isdigit() and 1 <= int(ans) <= len(sap_data):
                break
            msg.clear()
            msg.append(f"Возможно вводить значения только от 1 до {str(len(sap_data))}.")
            msg.append('Выберите пользователя, под которым хотим войти в систему')
            ans = print_log(msg, stop='Y')
        ans = int(ans) - 1
    else:
        ans = 0

    if v:
        msg.clear()
        msg.append(colored('Информация о запускаемой системе:', 'green'))
        sys_list.append([sap_data[ans][0], sap_data[ans][1], sap_data[ans][2], sap_data[ans][3]])
        answer = print_log(msg, sys_list, v, 'X')
        if answer:
            sys.exit()

    # Добавляем путь к командному файлу
    argument = [sapshcut_exe_path]

    # Добавляем номер системы
    item = '-system=' + sap_data[ans][0]
    argument.append(item)

    # Добавляем номер манданта
    client = sap_data[ans][1]
    # Если манданты имеею длину меньше чем 3 символа, например, 001, 002, то дополняем их лидирующими нулями
    # все осатльные системы, например, 100, остаются как есть.
    item = '-client=' + str.zfill(client, 3)
    argument.append(item)

    # Добавляем язык для входа. по умолчанию подставляетс-я RU, если не указано другое.
    item = '-language=' + l
    argument.append(item)

    # Добавляем пользователя.
    # можно вводить пользователя самостоятельно отличного от пользователя в БД
    if u:
        item = '-user=' + u
        argument.append(item)
    else:
        item = '-user=' + sap_data[ans][2]
        argument.append(item)

    # Добавляем пароль
    # можно вводить пароль самостоятельно отличный от пароля в БДe
    if pw:
        item = '-pw=' + pw
        argument.append(item)
    else:
        item = '-pw=' + Crypto.decrypto(sap_data[ans][3])
        argument.append(item)

    # Добавляем код транзакции
    if t:
        if p:
            param_data = db.query_param(str(t).upper())

            # TODO: сделать использование параметра коммады с параметрами.
            # sapshcut.exe -user="gababitskii" -pw="<f,bwrbq1" -system="AKE" -client="100" -command="*SE11 RSRD1-TBMA_VAL=VTBFHA;*"
            # используем -t для запуска транзакции и -v для передачи параметров. В зависимости от транзакции нужно держать список полей

            item = f"-command=\"*{t.upper()} {param_data[0][1]}={p}\""
            # item = '-command="*TM_52 VTGFHA-BUKRS=TRM1;"'  # VTGFHA-RFHA=100000000057;" '

            argument.append(item)
            print(item)
            item = '-type=transaction'
            argument.append(item)
        else:
            item = '-command=' + t
            argument.append(item)
            item = '-type=transaction'
            argument.append(item)

    # Окно на весь экран
    item = '-maxgui'
    argument.append(item)

    # Запускаем SAP
    ret = subprocess.call(argument)

    if ret:
        click.echo(ret)
        click.pause('Нажмите для продолжения ...')


@cli.command('db')
def database():
    """ Создание базы данных для хранеия информкции о SAP системах """

    db_name = Database.db_name
    ini_file = Config.ini_file

    config = Config()
    config.read()
    path_db = config.data['DATABASE']['path']

    # Проверяем путь к базе данных из конфига
    if os.path.isfile(path_db):
        click.echo(click.style('База данных уже существует \n', bg='black', fg='yellow'))
        click.pause('Нажмите для продолжения ...')
    else:
        eng = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(eng)

        click.echo(click.style('База данных создана \n', bg='black', fg='green'))
        click.echo('Путь: %s \n' % click.format_filename(db_name))
        click.echo(click.style('!!! Базу данных нужно хранить в защищенном хранилище \n', bg='red', fg='white'))
        click.echo(click.style(f'Путь к базе данных следует указать в {ini_file} \n', bg='black', fg='white'))
        click.pause('Нажмите для продолжения ...')


@cli.command('add')
@click.option('-system', prompt=True, help='система')
@click.option(
    '-mandant', prompt=True, help='мандант', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='пользователь')
@click.option(
    '-password',
    help='пароль',
    prompt=True,
    confirmation_prompt=True,
    hide_input=True,
)
def add(system, mandant, user, password):
    """ Добавление SAP систем в базу данных """

    client = str(mandant).zfill(3)

    db = Database()
    db.add(str(system).upper(), client, str(user).upper(), Crypto.encrypto(str.encode(password)))

    result = db.query(str(system).upper(), client, str(user).upper())

    if result:
        for item in result:
            msg.clear()
            msg.append(colored('Добавлена следующая система:', 'green'))
            sys_list.append([item[0], item[1], item[2]])
            print_log(msg, sys_list)
    else:
        click.echo(click.style('Не удалось добавить системы в базу данных ... \n', bg='red', fg='white'))
        click.pause('Нажмите для продолжения ...')


@cli.command('update')
@click.option('-system', prompt=True, help='система')
@click.option(
    '-mandant', prompt=True, help='мандант', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='пользователь')
@click.option(
    '-password',
    help='пароль',
    prompt=True,
    confirmation_prompt=True,
    hide_input=True
)
def update(system, mandant, user, password):
    """ Обновление пароля для SAP системы """
    client = str(mandant).zfill(3)

    db = Database()
    db.update(str(system).upper(), client, str(user).upper(), Crypto.encrypto(str.encode(password)))

    msg.clear()
    msg.append(colored('Пароль обновлен для следующей системы:', 'green'))
    sys_list.append([str(system).upper(), client, str(user).upper()])
    print_log(msg, sys_list)


@cli.command('delete')
@click.option('-system', prompt=True, help='система')
@click.option(
    '-mandant', prompt=True, help='мандант', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='пользователь')
def delete(system, mandant, user):
    """ Удаление указанной SAP системы из базы данных """
    client = str(mandant).zfill(3)

    db = Database()
    db.delete(str(system).upper(), client, str(user).upper())

    result = db.query(system, client, user, 'x')

    if not result:
        msg.clear()
        msg.append(colored('Удалена следующая система:', 'green'))
        sys_list.append([str(system).upper(), client, str(user).upper()])
        print_log(msg, sys_list)


@cli.command('ini')
def ini():
    """ Создание конфигурационного ini файла """

    config = Config()

    if config.exists():
        click.echo(click.style('INI файл уже существует \n', bg='black', fg='yellow'))
        click.pause('Нажмите для продолжения ...')
    else:
        config.create()


@cli.command('show')
@click.option('-s', required=False, help='показать выбранную систему')
@click.option('-all', is_flag=True, required=False, help='показать все системы')
@click.option('-v', help='показать пароли', is_flag=True)
def show(all, s, v):
    """ Информация о SAP системах находящихся в базе данных """

    sap_data = []
    if all:
        # Подсоединяемся к базе данных и запрашиваем данные по всем системам
        db = Database()
        sap_data = db.query()
    elif s:
        # Подсоединяемся к базе данных и запрашиваем данные по выбранной системе
        db = Database()
        sap_data = db.query(str(s).upper())

    msg.clear()
    msg.append(colored('Запрошенные системы:', 'green'))
    print_log(msg, sap_data, v)


@cli.command('keys')
def keys():
    """ Создание ключей шифрования """

    Crypto().generate_keys()


@cli.command('ver', help='Текущая версия SAP shortcut')
def ver():
    # Считываем конфигурационный файл
    config = Config()
    config.read()

    sapshcut_exe_path = config.data['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('sapshcut.exe'):
        msg.clear()
        msg.append(colored('в ini файле не найден путь к sapshcut.exe', 'yellow'))
        print_log(msg)
        sys.exit()

    # Добавляем путь к командному файлу
    argument = [sapshcut_exe_path]

    # Добавляем номер системы
    item = '-version'
    argument.append(item)

    # Запускаем SAP
    subprocess.call(argument)


@cli.command('help', help='SAP GUI shortcut help')
def hlp():
    # Считываем конфигурационный файл
    config = Config()
    config.read()

    sapshcut_exe_path = config.data['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('sapshcut.exe'):
        msg.clear()
        msg.append(colored('в ini файле не найден путь к sapshcut.exe', 'yellow'))
        print_log(msg)
        sys.exit()

    # Добавляем путь к командному файлу
    argument = [sapshcut_exe_path]

    # Добавляем номер системы
    item = '-help'
    argument.append(item)

    # Запускаем SAP
    subprocess.call(argument)


if __name__ == '__main__':
    sys.excepthook = show_exception_and_exit
    cli()
