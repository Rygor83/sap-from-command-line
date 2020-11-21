#  ------------------------------------------
#   Copyright (c) Rygor. 2019.
#  ------------------------------------------

import configparser
import ctypes
import functools
import gettext
import os
import subprocess
import sys

import click
from colorama import init
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from prettytable import PrettyTable
from sqlalchemy import Column, String, BLOB
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from termcolor import colored

public_file = 'public_key.txt'
private_file = 'private_key.txt'

msg = []
sys_list = []

Base = declarative_base()

init()


class Sap(Base):
    __tablename__ = 'sap'
    system_id = Column(String(3), primary_key=True)
    mandant_num = Column(String(3), primary_key=True)
    user_id = Column(String(10), primary_key=True)
    password = Column(BLOB)


def print_sys_table(systems: list, v: bool = 0):
    # TODO: Сделать функцию динамическую, чтобы можно было засовывать разные заголовки

    header = ['№', _('Система'), _('Мандант'), _('Пользователь')]
    if v:
        header.append(_('Пароль'))
    t = PrettyTable(header)
    count = 0
    for system in systems:
        count = count + 1
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
        return input(_('нажмите Enter или любой текст для выхода: '))
    elif stop == 'Y':
        ans = input('> ')
        return ans
    elif stop == 'Z':
        return
    else:
        click.echo()
        return click.pause(_('нажмите Enter ...'))


class Database(object):
    """
    Класс для работы с базой данных
    """

    def __init__(self):

        if check_existence('.db'):
            conf = Config()
            conf.get_config()
            path_db = conf.config['DATABASE']['path']
            engine = create_engine(f"sqlite:///{path_db}")
            session = sessionmaker(bind=engine)
            self.session = session()
        else:
            msg.clear()
            msg.append(colored(_('Базы данных не существует. Для создания запустите команду "db" '), 'yellow'))
            print_log(msg)
            sys.exit()

    def query(self, system='', mandant='', user='', check=''):
        """
        Методе для запросов информации о SAP системе
        :param system: номер SAP системы;
        :param mandant: номер манданта;
        :param user: пользователь;
        :param check: флаг проверки выполнена ли операция (добавление, удаление) без уведомлений о результатах поиска;
        :return: информация о системе (система, мандант, пользователь и пароль);
        """

        # TODO: попробовать внедрить namedtuple
        #       from collections import namedtuple

        client = str(mandant).zfill(3)

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password)
        if system:
            query = query.filter_by(system_id=system)
        if mandant:
            query = query.filter_by(mandant_num=client)
        if user:
            query = query.filter_by(user_id=user)

        result = query.all()

        if result:
            return result
        else:
            if not check:
                msg.clear()
                msg.append(colored(_('По указанным данным найти ничего не получилось'), 'yellow'))
                sys_list.append([system, client, user])
                print_log(msg, sys_list)
                sys.exit()

    def add(self, system, mandant, user, password):
        """
        Класс для добавления информации о системе
        :param system:
        :param mandant:
        :param user:
        :param password:
        :return:
        """

        client = str(mandant).zfill(3)

        sap_info = Sap(
            system_id=system, mandant_num=client, user_id=user, password=password)

        self.session.add(sap_info)
        try:
            self.session.commit()
        except IntegrityError:
            msg.clear()
            msg.append(colored(_('Данные уже существуют в базе данных:'), 'yellow'))
            sys_list.append([system, client, user])
            print_log(msg, sys_list)
            sys.exit()

    def update(self, system, mandant, user, password):
        client = str(mandant).zfill(3)

        result = self.filter(client, system, user)

        if result:
            result.password = password
            self.session.commit()
        else:
            msg.clear()
            msg.append(colored(_('Ничего не найден для удаления по введенным данным:'), 'yellow'))
            sys_list.append([system, client, user])
            print_log(msg, sys_list)
            sys.exit()

    def delete(self, system, mandant, user):
        client = str(mandant).zfill(3)
        result = self.filter(client, system, user)
        self.session.delete(result)
        self.session.commit()

    def filter(self, mandant, system, user):
        client = str(mandant).zfill(3)
        query = self.session.query(Sap)
        try:
            result = query.filter(Sap.system_id == system, Sap.mandant_num == client,
                                  Sap.user_id == user).one()
        except NoResultFound:
            msg.clear()
            msg.append(colored(_('Ничего не найден для удаления по введенным данным:'), 'yellow'))
            sys_list.append([system, client, user])
            print_log(msg, sys_list)
            sys.exit()
        return result


class Config(object):
    def __init__(self):
        self.config = {'CONNECTION': {}, 'APPLICATION': {}, 'KEYS': {}, 'LANGUAGE': {}}

    @functools.lru_cache()
    def get_config(self):

        ini_file = f"{os.path.splitext(os.path.basename(__file__))[0]}.ini"
        if os.path.isfile(ini_file) and os.stat(ini_file).st_size != 0:
            path = os.path.join(os.path.dirname(__file__), ini_file)
        else:
            msg.clear()
            # TODO: переделать сообщиние, чтоб мол нет доступа к ини файлу т.к. его или не существует, или нет доступа.
            # TODO: Сделать не только уведомление, но так же попытка запустить контейнер, где располагается БД
            msg.append(colored(_('Не удалось получить нужные параметры т.к. ini файла не существует.'), 'yellow'))
            msg.append(_('Для создания запустите команду "ini" и укажите в созданном файле все требуетмые параметры'))
            print_log(msg)
            sys.exit()

        config = configparser.ConfigParser()

        read = config.read(path)
        if not read:
            msg.clear()
            msg.append(colored(_('Не удалось прочитать ini файл'), 'yellow'))
            print_log(msg)
        else:
            self.config['DATABASE'] = config['DATABASE']
            self.config['APPLICATION'] = config['APPLICATION']
            self.config['KEYS'] = config['KEYS']
            self.config['LANGUAGE'] = config['LANGUAGE']


# noinspection PyShadowingNames
class Crypto(object):
    @staticmethod
    def generate_keys():
        """
        Создание ключей шифрования: публичный ключ и приватный ключа
        """

        conf = Config()
        conf.get_config()
        path_public_key = conf.config['KEYS'][public_file]
        path_private_key = conf.config['KEYS'][private_file]

        if not os.path.isfile(path_public_key) and not os.path.isfile(path_private_key):
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            Crypto.save_key(private_pem, private_file)

            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
            Crypto.save_key(public_pem, public_file)
            msg.clear()
            msg.append(colored(_(f"Ключи шифрования созданы: {public_file} и {private_file}"), 'green'))
            msg.append(_('Необходимо указать их расположение в файле *.ini'))
            msg.append(
                colored(_(f"Файл {private_file} должен находиться в зашифрованном хранилище"), 'white', 'on_red'))
            print_log(msg)
        else:
            msg.clear()
            msg.append(colored(_("Ключи шифрования уже созданы"), 'yellow'))
            print_log(msg)
            sys.exit()

    @staticmethod
    def save_key(pem, file_name):
        with open(file_name, "w") as file:
            for item in pem.splitlines():
                # print(item)
                file.write(item.decode() + '\n')

    @staticmethod
    def encrypto(password):
        public_key_file = Crypto.get_key(public_file)

        try:
            with open(public_key_file, "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())
        except FileNotFoundError:
            msg.clear()
            msg.append(colored(_('Публичный ключ шифрования не доступен. Проверьте доступ'), 'yellow'))
            print_log(msg)
            sys.exit()

        encrypted_data = public_key.encrypt(
            password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data

    @staticmethod
    def decrypto(encrypted_password):
        private_key_file = Crypto.get_key(private_file)

        try:
            with open(private_key_file, "rb") as key_file:
                private_key = serialization.load_pem_private_key(key_file.read(), password=None,
                                                                 backend=default_backend())
        except FileNotFoundError:
            msg.clear()
            msg.append(colored(_('Приватный ключ шифрования не доступен. Проверьте доступ'), 'yellow'))
            print_log(msg)
            sys.exit()

        decrypted_data = private_key.decrypt(encrypted_password,
                                             padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None)).decode()
        return decrypted_data

    @staticmethod
    def get_key(key_name):
        conf = Config()
        conf.get_config()
        key_file = conf.config['KEYS'][key_name]
        if not key_file.endswith('.txt'):
            msg.clear()
            msg.append(colored(_(f"в ini файле не найден путь к {key_name} ключу шифрования"), 'yellow'))
            print_log(msg)
            sys.exit()
        return key_file


def check_existence(file_extension) -> bool:
    if file_extension == '.db':
        conf = Config()
        conf.get_config()
        path_db = conf.config['DATABASE']['path']
        if os.path.isfile(path_db):
            file_exists = True
            return file_exists

    if os.path.isfile(f"{os.path.splitext(os.path.basename(__file__))[0]}{file_extension}"):
        file_exists = True
        return file_exists
    else:
        file_exists = False
        return file_exists


if check_existence('.ini'):
    conf = Config()
    conf.get_config()
    language = conf.config['LANGUAGE']['language']
else:
    language = 'EN'
lng = gettext.translation('sap_cmd', localedir='locale', languages=[language], fallback=True)
lng.install()


@click.group()
def cli():
    """ Скрипт для запуска SAP систем из командной строки """


# noinspection PyShadowingNames
@cli.command('logon')
def logon():
    """ Запуск SAPLogon """

    # Считываем конфигурационный файл
    conf = Config()
    conf.get_config()

    # Запускаем saplogon.exe
    saplogon_exe_path = conf.config['APPLICATION']['sap']
    if not str(saplogon_exe_path).endswith('saplogon.exe'):
        msg.clear()
        msg.append(colored(_('в ini файле не найден путь к saplogon.exe'), 'yellow'))
        print_log(msg)
        sys.exit()

    click.launch(saplogon_exe_path)


@cli.command('pw')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', help=_('пользователь'))
def pw(system, mandant, u=''):
    """ Копирует пароль от заданной системы в буфер обмена. Стирает буфер обмена через 30 секунд \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    # TODO: Реализова на подобии команды RUN
    #       Как копировать в буфер обмена и как стирать буфер обмена


# noinspection PyShadowingNames,PyUnboundLocalVariable,PyTypeChecker
@cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', help=_('пользователь'))
@click.option('-pw', help=_('пароль'))
@click.option('-l', help=_('язык входа'), default='RU')
@click.option('-v', help=_('показать параметры запуска'), is_flag=True, type=click.BOOL)
@click.option('-t', help=_('код транзакции'))
@click.option('-p', help=_('параметры для транзакции'))
def run(system, mandant, u='', pw='', l='RU', v=0, t='', p=''):
    """ Запуск указанной SAP системы \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    # Считываем конфигурационный файл
    conf = Config()
    conf.get_config()

    sapshcut_exe_path = conf.config['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('sapshcut.exe'):
        msg.clear()
        msg.append(colored(_('в ini файле не найден путь к sapshcut.exe'), 'yellow'))
        print_log(msg)
        sys.exit()

    # Подсоединяемся к базе данных и запрашиваем данные
    msg.append(_(f"Пробуем запустить {str(system).upper()} {mandant if mandant else ''} {t.upper() if t else ''}"))
    print_log(msg, stop='Z')

    db = Database()
    sap_data = db.query(str(system).upper(), mandant, str(u).upper() if u else '')

    ans = ''
    if len(sap_data) >= 2:
        msg.clear()
        msg.append(_('Выбраны следующие пользователи: '))
        print_log(msg, sap_data, stop='Z')

        while not ans.isdigit() or int(ans) > len(sap_data) or int(ans) < 1:
            if ans.isdigit() and 1 <= int(ans) <= len(sap_data):
                break
            msg.clear()
            msg.append(_(f"Возможно вводить значения только от 1 до {str(len(sap_data))}."))
            msg.append(_('Выберите пользователя, под которым хотим войти в систему'))
            ans = print_log(msg, stop='Y')
        ans = int(ans) - 1
    else:
        ans = 0

    if v:
        msg.clear()
        msg.append(colored(_('Информация о запускаемой системе:'), 'green'))
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
            # TODO: сделать использование параметра коммады с параметрами.
            # sapshcut.exe -user="gababitskii" -pw="<f,bwrbq1" -system="AKE" -client="100" -command="*SE11 RSRD1-TBMA_VAL=VTBFHA;*"
            # используем -t для запуска транзакции и -v для передачи параметров. В зависимости от транзакции нужно держать список полей

            parameter_list = p.split('+')
            # item = f"-command=\"{t.upper()} VTGFHA-BUKRS={parameter_list[0]};VTGFHA-RFHA={parameter_list[1]};\""
            item = '-command="*TM_52 VTGFHA-BUKRS=TRM1;"'  # VTGFHA-RFHA=100000000057;" '

            argument.append(item)
            print(item)
            # item = '-type=transaction'
            # argument.append(item)
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
        print(ret)
        input(_('нажмите Enter ...'))


@cli.command('db')
def database():
    """ Создание базы данных для хранеия информкции о SAP системах """

    file_exists = check_existence('.db')

    if file_exists:
        msg.clear()
        msg.append(colored(_('База данных уже существует.'), 'yellow'))
        print_log(msg)
    else:
        db_name = f"{os.path.splitext(os.path.basename(__file__))[0]}.db"

        eng = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(eng)
        msg.clear()
        msg.append(colored(_('База данных создана'), 'green'))
        msg.append(_('Если база данных будет перемещена, то следует указать ее путь в *.ini файле'))
        print_log(msg)


@cli.command('add')
@click.option('-system', prompt=True, help=_('система'))
@click.option(
    '-mandant', prompt=True, help=_('мандант'), type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help=_('пользователь'))
@click.option(
    '-password',
    help=_('пароль'),
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
            msg.append(colored(_('Добавлена следующая система:'), 'green'))
            sys_list.append([item[0], item[1], item[2]])
            print_log(msg, sys_list)
    else:
        msg.clear()
        msg.append(colored(_('Что-то пошло не так ...'), 'white', 'on_red'))
        print_log(msg)


@cli.command('update')
@click.option('-system', prompt=True, help=_('система'))
@click.option(
    '-mandant', prompt=True, help=_('мандант'), type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help=_('пользователь'))
@click.option(
    '-password',
    help=_('пароль'),
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
    msg.append(colored(_('Пароль обновлен для следующей системы:'), 'green'))
    sys_list.append([str(system).upper(), client, str(user).upper()])
    print_log(msg, sys_list)


@cli.command('delete')
@click.option('-system', prompt=True, help=_('система'))
@click.option(
    '-mandant', prompt=True, help=_('мандант'), type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help=_('пользователь'))
def delete(system, mandant, user):
    """ Удаление указанной SAP системы из базы данных """
    client = str(mandant).zfill(3)

    db = Database()
    db.delete(str(system).upper(), client, str(user).upper())

    result = db.query(system, client, user, 'x')

    if not result:
        msg.clear()
        msg.append(colored(_('Удалена следующая система:'), 'green'))
        sys_list.append([str(system).upper(), client, str(user).upper()])
        print_log(msg, sys_list)


@cli.command('ini')
def ini():
    """ Создание конфигурационного ini файла """

    file_exists = check_existence('.ini')

    if file_exists:
        msg.clear()
        msg.append(colored(_('ini файл уже существует.'), 'yellow'))
        print_log(msg)
    else:
        config = configparser.ConfigParser()
        config['DATABASE'] = {'path': f"{os.path.splitext(os.path.basename(__file__))[0]}.db"}

        config['APPLICATION'] = {'command_line': _('путь до файла sapshcut.exe'),
                                 'sap': _('путь до файла saplogon.exe')}

        config['KEYS'] = {public_file: _('путь до публичного ключа'),
                          private_file: _('путь до приватного ключа. ключ хранить в защищенном хранилище')}

        # Определение языка
        windll = ctypes.windll.kernel32
        lng_code = windll.GetUserDefaultUILanguage()
        if lng_code == 1049:
            ini_lang = 'RU'
        else:
            ini_lang = 'EN'
        config['LANGUAGE'] = {'language': ini_lang}

        print(os.path.basename(__file__))
        with open(f"{os.path.splitext(os.path.basename(__file__))[0]}.ini", 'w') as configfile:
            config.write(configfile)

        msg.clear()
        msg.append(colored(_('ini файл создан.'), 'green'))
        msg.append(_('!!! Заполните все требуемые параметры в файле !!!'))
        print_log(msg)


@cli.command('show')
@click.option('-s', required=False, help=_('показать выбранную систему'))
@click.option('-all', is_flag=True, required=False, help=_('показать все системы'))
@click.option('-v', help=_('показать пароли'), is_flag=True)
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
    msg.append(colored(_('Запрошенные системы:'), 'green'))
    print_log(msg, sap_data, v)


@cli.command('keys')
def keys():
    """ Создание ключей шифрования """

    Crypto().generate_keys()


@cli.command('ver', help=_('Текущая версия SAP shortcut'))
def ver():
    # Считываем конфигурационный файл
    conf = Config()
    conf.get_config()

    sapshcut_exe_path = conf.config['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('sapshcut.exe'):
        msg.clear()
        msg.append(colored(_('в ini файле не найден путь к sapshcut.exe'), 'yellow'))
        print_log(msg)
        sys.exit()

    # Добавляем путь к командному файлу
    argument = [sapshcut_exe_path]

    # Добавляем номер системы
    item = '-version'
    argument.append(item)

    # Запускаем SAP
    subprocess.call(argument)


@cli.command('help', help=_('SAP GUI shortcut help'))
def hlp():
    # Считываем конфигурационный файл
    conf = Config()
    conf.get_config()

    sapshcut_exe_path = conf.config['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('sapshcut.exe'):
        msg.clear()
        msg.append(colored(_('в ini файле не найден путь к sapshcut.exe'), 'yellow'))
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
    cli()

# функция перевода через модуль gettext
_ = lambda s: s
