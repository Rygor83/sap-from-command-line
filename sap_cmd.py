import configparser
import os
import subprocess
import sys
import gettext
import click
from sqlalchemy import Column, String, BLOB
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

Base = declarative_base()


class Sap(Base):
    __tablename__ = 'sap'
    system_id = Column(String(3), primary_key=True)
    mandant_num = Column(String(3), primary_key=True)
    user_id = Column(String(10), primary_key=True)
    password = Column(BLOB)


def print_log(message, system='', mandant='', user='', password='', stop=''):
    print('\n')
    print(message)
    if system:
        print(_('Система:'), '\t', system)
    if mandant:
        print(_('Мандант:'), '\t', mandant)
    if user:
        print(_('Пользователь:'), '\t', user)
    if password:
        print(_('Пароль:'), '\t', password)
    print('\n')
    if stop:
        return input(_('нажмите Enter или любой текст для выхода: '))
    else:
        return input(_('нажмите Enter ...'))


class Database(object):
    def __init__(self):

        if os.path.isfile(f"{os.path.splitext(os.path.basename(__file__))[0]}.db"):
            engine = create_engine(f"sqlite:///{os.path.splitext(os.path.basename(__file__))[0]}.db")
            session = sessionmaker(bind=engine)
            self.session = session()
        else:
            print_log(_('Базы данных не существует. Для создания запустите команду "db" '))
            sys.exit()

    def query(self, system='', mandant='', user='', check=''):

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password)
        if system:
            query = query.filter_by(system_id=system)
        if mandant:
            query = query.filter_by(mandant_num=mandant)
        if user:
            query = query.filter_by(user_id=user)

        result = query.all()

        if result:
            return result
        else:
            if not check:
                print_log(_('По указанным данным найти ничего не получилось'), system, mandant, user)
                sys.exit()

    def add(self, system, mandant, user, password):
        sap_info = Sap(
            system_id=system, mandant_num=mandant, user_id=user, password=password)

        self.session.add(sap_info)
        try:
            self.session.commit()
        except IntegrityError:
            print_log(_('Данные уже существуют в базе данных:'), system, mandant, user)
            sys.exit()

    def update(self, system, mandant, user, password):
        result = self.filter(mandant, system, user)

        if result:
            result.password = password
            self.session.commit()
        else:
            print_log(_('Ничего не найден для удаления по введенным данным:'), system, mandant, user)
            sys.exit()

    def delete(self, system, mandant, user):
        result = self.filter(mandant, system, user)
        self.session.delete(result)
        self.session.commit()

    def filter(self, mandant, system, user):
        query = self.session.query(Sap)
        try:
            result = query.filter(Sap.system_id == system, Sap.mandant_num == mandant,
                                  Sap.user_id == user).one()
        except NoResultFound:
            print_log(_('Ничего не найден для удаления по введенным данным:'), system, mandant, user)
            sys.exit()
        return result


class Config(object):
    def __init__(self):
        self.config = {'CONNECTION': {}, 'APPLICATION': {}, 'KEYS': {}, 'LANGUAGE': {}}

    def get_config(self):

        ini_file = f"{os.path.splitext(os.path.basename(__file__))[0]}.ini"
        if os.path.isfile(ini_file) and os.stat(ini_file).st_size != 0:
            path = os.path.join(os.path.dirname(__file__), ini_file)
        else:
            print_log(_('''
            Не удалось получить нужные параметры т.к. ini файла не существует. \n
            Для создания запустите команду "ini" и укажите в созданном файле все требуетмые параметры \n
            '''))
            sys.exit()

        config = configparser.ConfigParser()

        read = config.read(path)
        if not read:
            print_log(_('Не удалось прочитать ini файл'))
        else:
            self.config['CONNECTION'] = config['CONNECTION']
            self.config['APPLICATION'] = config['APPLICATION']
            self.config['KEYS'] = config['KEYS']
            self.config['LANGUAGE'] = config['LANGUAGE']


# noinspection PyShadowingNames
class Crypto(object):
    @staticmethod
    def generate_keys():
        if not os.path.isfile(f"{os.path.dirname(__file__)}\public_key.txt"):
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            Crypto.save_key(private_pem, 'private_key.txt')

            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
            Crypto.save_key(public_pem, 'public_key.txt')
            print_log(_("Ключи шифрования созданы."))
        else:
            print_log(_("Ключи шифрования уже созданы"))
            sys.exit()

    @staticmethod
    def save_key(pem, file_name):
        with open(file_name, "w") as file:
            for item in pem.splitlines():
                print(item)
                file.write(item.decode() + '\n')

    @staticmethod
    def encrypto(password):
        public_key_file = Crypto.get_key('public_key')

        try:
            with open(public_key_file, "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())
        except FileNotFoundError:
            print_log(_('Приватный ключе не доступен'))
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
        private_key_file = Crypto.get_key('private_key')

        try:
            with open(private_key_file, "rb") as key_file:
                private_key = serialization.load_pem_private_key(key_file.read(), password=None,
                                                                 backend=default_backend())
        except FileNotFoundError:
            print_log(_('Приватный ключе не доступен'))
            sys.exit()

        decrypted_data = private_key.decrypt(encrypted_password,
                                             padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None)).decode()
        return decrypted_data

    @staticmethod
    def get_key(key_name):
        cfg = Config()
        cfg.get_config()
        key_file = cfg.config['KEYS'][key_name]
        if not key_file.endswith('.txt'):
            print_log(_(f"в ini файле не найден путь к {key_name} ключу шифрования"))
            sys.exit()
        return key_file


lng = gettext.translation('sap_cmd', localedir='locale', languages=['en'], fallback=True)
lng.install()


def check_existence(file_extension) -> bool:
    # check if db exists
    file_exists = False
    for fname in os.listdir('.'):
        if fname.endswith(file_extension):
            file_exists = True
    return file_exists


@click.group()
def cli():
    """ Скрипт для запуска SAP систем из командной строки """


# noinspection PyShadowingNames
@cli.command('logon')
def logon():
    """ Запуск SAPLogon """

    # Считываем конфигурационный файл
    cfg = Config()
    cfg.get_config()

    # Запускаем saplogon.exe
    saplogon_exe_path = cfg.config['APPLICATION']['sap']
    if not str(saplogon_exe_path).endswith('saplogon.exe'):
        print_log(_('в ini файле не найден путь к saplogon.exe'))
        sys.exit()

    click.launch(saplogon_exe_path)


# noinspection PyShadowingNames,PyUnboundLocalVariable
@cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', help=_('пользователь'))
@click.option('-p', help=_('пароль'))
@click.option('-l', help=_('язык входа'), default='RU')
@click.option('-v', help=_('показать параметры запуска'), is_flag=True)
@click.option('-t', help=_('код транзакции'))
def run(system, mandant, u='', p='', l='RU', v='', t=''):
    """ Запуск указанной SAP системы \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

    # Считываем конфигурационный файл
    cfg = Config()
    cfg.get_config()

    sapshcut_exe_path = cfg.config['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('sapshcut.exe'):
        print_log(_('в ini файле не найден путь к sapshcut.exe'))
        sys.exit()

    # Подсоединяемся к базе данных и запрашиваем данные
    print(_('Пробуем запустить'), str(system).upper(), '\n')

    db = Database()
    sap_data = db.query(system, mandant, u)

    if len(sap_data) >= 2:
        i = 0
        message = ''
        for item in sap_data:
            i += 1
            message += f"{str(i)}. {item[0]}-{item[1]}: {item[2]} \n"
        print(_('Выбраны следующие пользователи: '))
        print(message)
        print(_('Выберите пользователя под которым хотим войти в систему.'))
        print(_('Допустимый ввод - индекс от 1 до'), str(len(sap_data)), ': "')
        ans = input(': ')
        while not ans.isdigit() or int(ans) > len(sap_data) or int(ans) < 1:
            print(_("Возможно вводить значения только от 1 до"), str(len(sap_data)), ".")
            ans = input(_('Выберите пользователя под которым хотим войти в систему: '))
        ans = int(ans) - 1
    else:
        ans = 0

    if v:
        answer = print_log('', sap_data[ans][0], sap_data[ans][1], sap_data[ans][2],
                           Crypto.decrypto(sap_data[ans][3]), 'x')
        if answer:
            sys.exit()

    # Добавляем путь к командному файлу
    argument = [sapshcut_exe_path]

    # Добавляем номер системы
    item = '-system=' + sap_data[ans][0].upper()
    argument.append(item)

    # Добавляем номер манданта
    item = '-client=' + sap_data[ans][1].upper()
    argument.append(item)

    # Добавляем язык для входа. по умолчанию подставляется RU, если не указано другое.
    item = '-language=' + l
    argument.append(item)

    # Добавляем пользователя.
    # можно вводить пользователя самостоятельно отличного от пользователя в БД
    if u:
        item = '-user=' + u
        argument.append(item)
    else:
        item = '-user=' + sap_data[ans][2].upper()
        argument.append(item)

    # Добавляем пароль
    # можно вводить пароль самостоятельно отличный от пароля в БДe
    if p:
        item = '-pw=' + p
        argument.append(item)
    else:
        item = '-pw=' + Crypto.decrypto(sap_data[ans][3])
        argument.append(item)

    # Добавляем код транзакции
    if t:
        item = '-command=' + t
        argument.append(item)
        item = '-type=transaction'
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
        print_log(_('База данных уже существует.'))
    else:
        db_name = f"{os.path.splitext(os.path.basename(__file__))[0]}.db"

        eng = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(eng)
        print_log(_('База данных создана'))


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
    # hide_input=True,
)
def add(system, mandant, user, password):
    """ Добавление SAP систем в базу данных """

    db = Database()
    db.add(system, mandant, user, Crypto.encrypto(str.encode(password)))

    result = db.query(system, mandant, user)

    if result:
        for item in result:
            print_log(_('Добавлена следующая система:'), item[0], item[1], item[2])
    else:
        print_log(_('Что-то пошло не так ...'))


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
    # hide_input=True
)
def update(system, mandant, user, password):
    """ Обновление пароля для SAP системы """

    db = Database()
    db.update(system, mandant, user, Crypto.encrypto(str.encode(password)))
    print_log(_('Пароль обновлен'))


@cli.command('delete')
@click.option('-system', prompt=True, help=_('система'))
@click.option(
    '-mandant', prompt=True, help=_('мандант'), type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help=_('пользователь'))
def delete(system, mandant, user):
    """ Удаление указанной SAP системы из базы данных """

    db = Database()
    db.delete(system, mandant, user)

    result = db.query(system, mandant, user, 'x')

    if not result:
        print_log(_('Удалена следующая система:'), system, mandant, user)


@cli.command('ini')
def ini():
    """ Создание конфигурационного ini файла """

    file_exists = check_existence('.ini')

    if file_exists:
        print_log(_('ini файл уже существует.'))
    else:
        config = configparser.ConfigParser()
        config['CONNECTION'] = {
            'user': 'user_name',
            'password': 'password',
            'database': 'db',
            'host': 'host',
            'port': 'port',
            'charset': 'ch'
        }

        config['APPLICATION'] = {'command_line': _('путь до файла sapshcut.exe'),
                                 'sap': _('путь до файла saplogon.exe')}

        config['KEYS'] = {'public_key': _('путь до публичного ключа'),
                          'private_key': _('путь до приватного ключа. ключ хранить в защищенном хранилище')}

        config['LANGUAGE'] = {'language': _('язык интерфейса: или RU (русский), или EN (английский язык)')}

        print(os.path.basename(__file__))
        with open(f"{os.path.splitext(os.path.basename(__file__))[0]}.ini", 'w') as configfile:
            config.write(configfile)

        print_log(_('ini файл создан. \n !!! Заполните все требуемые параметры в файле !!!'))


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
        sap_data = db.query(s)

    for system in sap_data:
        print(_('Система: '), str(system[0]).upper(), '\t', _('Мандант: '), str(system[1]).upper(),
              '\t', _('Пользователь: '), str(system[2]).upper(),
              '\t', _('Пароль: ') if v else '', Crypto.decrypto(system[3]) if v else '')
    print_log('')


@cli.command('key')
def key():
    """ Создание ключей шифрования """

    Crypto().generate_keys()
    print_log(_('''Ключи шифрования созданы: public_key.txt и private_key.txt \n 
                   Необходимо указать их расположение в файле *.ini \n 
                   Файл private_key.txt должен находиться в зашифрованном хранилище'''))


if __name__ == '__main__':
    cli()

# функция перевода через модуль gettext
_ = lambda s: s
