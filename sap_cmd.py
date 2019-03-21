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


class Database(object):
    def __init__(self):

        if os.path.isfile(f"{os.path.splitext(os.path.basename(__file__))[0]}.db"):
            engine = create_engine(f"sqlite:///{os.path.splitext(os.path.basename(__file__))[0]}.db")
            session = sessionmaker(bind=engine)
            self.session = session()
        else:
            print(_('Базы данных не существует. Для создания запустите команду "db" '))
            input(_('нажмите Enter ...'))
            sys.exit()

    def query(self, system='', mandant='', user=''):

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
            print(_('По указанным данным найти ничего не получилось'))
            print(_('Система:'), '\t', system)
            print(_('Мандант:'), '\t', mandant)
            print(_('Пользователь:'), '\t', user)
            input(_('нажмите Enter ...'))
            sys.exit()

    def add(self, system, mandant, user, password):
        sap_info = Sap(
            system_id=system, mandant_num=mandant, user_id=user, password=password)

        self.session.add(sap_info)
        self.session.commit()

    def update(self, system, mandant, user, password):
        query = self.session.query(Sap)
        result = query.filter(Sap.system_id == system, Sap.mandant_num == mandant,
                              Sap.user_id == user).first()
        result.password = password
        self.session.commit()

    def delete(self, system, mandant, user):
        query = self.session.query(Sap)
        result = query.filter(Sap.system_id == system, Sap.mandant_num == mandant,
                              Sap.user_id == user).one()
        self.session.delete(result)
        self.session.commit()


class Config(object):
    def __init__(self):
        self.config = {'CONNECTION': {}, 'APPLICATION': {}, 'KEYS': {}, 'LANGUAGE': {}}

    def get_config(self):

        ini_file = f"{os.path.splitext(os.path.basename(__file__))[0]}.ini"
        if os.path.isfile(ini_file) and os.stat(ini_file).st_size != 0:
            path = os.path.join(os.path.dirname(__file__), ini_file)
        else:
            print(_('Не удалось получить нужные параметры т.к. ini файла не существует.'))
            print(_('Для создания запустите команду "ini" и укажите в созданном файле все требуетмые параметры'))
            input(_('нажмите Enter ...'))
            sys.exit()

        config = configparser.ConfigParser()

        read = config.read(path)
        if not read:
            print(_('Не удалось прочитать ini файл'))
            input(_('нажмите Enter ...'))
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
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            for item in pem.splitlines():
                print(item)
            with open("private_key.txt", "w") as file:
                for item in pem.splitlines():
                    file.write(item.decode() + '\n')

            public_key = private_key.public_key()
            pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PublicFormat.SubjectPublicKeyInfo)
            for item in pem.splitlines():
                print(item)
            with open("public_key.txt", "w") as file:
                for item in pem.splitlines():
                    file.write(item.decode() + '\n')
            print(_("Ключи шифрования созданы."))
            input(_("нажмите Enter ..."))
        else:
            print(_("Ключи шифрования уже созданы"))
            input(_("нажмите Enter ..."))

    @staticmethod
    def encrypto(password):
        cfg = Config()
        cfg.get_config()

        public_key_file = cfg.config['KEYS']['public_key']
        if not public_key_file.endswith('.txt'):
            print(_('в ini файле не найден путь к публичному ключу шифрования'))
            input(_('нажмите Enter ...'))
            sys.exit()

        with open(public_key_file, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())

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
        cfg = Config()
        cfg.get_config()

        private_key_file = cfg.config['KEYS']['private_key']
        if not private_key_file.endswith('.txt'):
            print(_('в ini файле не найден путь к приватному ключу шифрования'))
            input(_('нажмите Enter ...'))
            sys.exit()

        with open(private_key_file, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())

        decrypted_data = private_key.decrypt(encrypted_password,
                                             padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None)).decode()
        return decrypted_data


cfg = Config()
cfg.get_config()
lang = cfg.config['LANGUAGE']['language']
lng = gettext.translation('sap_cmd', localedir='locale', languages=[lang], fallback=True)
lng.install()


@click.group()
def cli():
    _(""" Скрипт для запуска SAP систем из командной строки """)


@cli.command('logon')
def logon():
    _(""" Запуск SAPLogon """)

    # Считываем конфигурационный файл
    cfg = Config()
    cfg.get_config()

    # Запускаем saplogon.exe
    saplogon_exe_path = cfg.config['APPLICATION']['sap']
    if not saplogon_exe_path.endswith('.exe'):
        print('\n', _('в ini файле не найден путь к saplogon.exe'))
        input(_('нажмите Enter ...'))
        sys.exit()

    click.launch(saplogon_exe_path)


@cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', help='_(пользователь)')
@click.option('-p', help='_(пароль)')
@click.option('-l', help='_(язык входа)', default='RU')
@click.option('-v', help='_(показать параметры запуска)', is_flag=True)
@click.option('-t', help='_(код транзакции)')
def run(system, mandant, u='', p='', l='RU', v='', t=''):
    _(""" Запуск указанной SAP системы \n
        Обязательные параметры: 1. система, 2. мандант (не обязательно) """)

    # Считываем конфигурационный файл
    cfg = Config()
    cfg.get_config()

    sapshcut_exe_path = cfg.config['APPLICATION']['command_line']
    if not sapshcut_exe_path.endswith('.exe'):
        print('\n', _('в ini файле не найден путь к sapshcut.exe'))
        input(_('нажмите Enter ...'))
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
        print(_('Система:'), '\t', sap_data[ans][0])
        print(_('Мандант:'), '\t', sap_data[ans][1])
        print(_('Пользователь:'), '\t', sap_data[ans][2])
        print(_('Пароль:'), '\t', Crypto.decrypto(sap_data[ans][3]))
        answer = input(_('нажмите Enter или любой текст для выхода: '))
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
    # можно вводить пароль самостоятельно отличный от пароля в БД
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
    _(""" Создание базы данных для хранеия информкции о SAP системах """)

    # check if db exists
    file_exists = False
    for fname in os.listdir('.'):
        if fname.endswith('.db'):
            file_exists = True

    if file_exists:
        print(_('База данных уже существует.'))
        input(_('нажмите Enter ...'))
    else:
        db_name = f"{os.path.splitext(os.path.basename(__file__))[0]}.db"

        eng = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(eng)
        print(_('База данных создана: '), db_name)
        input(_('нажмите Enter ...'))


@cli.command('add')
@click.option('-system', prompt=True, help='_(система)')
@click.option(
    '-mandant', prompt=True, help='_(мандант)', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='_(пользователь)')
@click.option(
    '-password',
    help='_(пароль)',
    prompt=True,
    confirmation_prompt=True,
    hide_input=True
)
def add(system, mandant, user, password):
    _(""" Добавление SAP систем в базу данных """)

    db = Database()
    db.add(system, mandant, user, Crypto.encrypto(str.encode(password)))

    result = db.query(system, mandant, user)

    for item in result:
        print('\n', _('Добавлена следующая система:'))
        print(_('Система:'), '\t', item[0])
        print(_('Мандант:'), '\t', item[1])
        print(_('Пользователь:'), '\t', item[2])
        input(_('нажмите Enter ...'))
    else:
        print(_('Что-то пошло не так ...'))


@cli.command('update')
@click.option('-system', prompt=True, help='_(система)')
@click.option(
    '-mandant', prompt=True, help='_(мандант)', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='_(пользователь)')
@click.option(
    '-password',
    help='_(пароль)',
    prompt=True,
    confirmation_prompt=True,
    hide_input=True
)
def update(system, mandant, user, password):
    _(""" Обновление пароля для SAP системы """)

    db = Database()
    db.update(system, mandant, user, Crypto.encrypto(str.encode(password)))
    print('\n', _('Пароль обновлен'))
    input(_('нажмите Enter ...'))


@cli.command('delete')
@click.option('-system', prompt=True, help='_(система)')
@click.option(
    '-mandant', prompt=True, help='_(мандант)', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='_(пользователь)')
def delete(system, mandant, user):
    _(""" Удаление указанной SAP системы из базы данных """)

    db = Database()
    db.delete(system, mandant, user)

    result = db.query(system, mandant, user)

    if not result:
        print('\n', _('Удалена следующая система:'))
        print(_('Система:'), '\t', system)
        print(_('Мандант:'), '\t', mandant)
        print(_('Пользователь:'), '\t', user)
        input(_('нажмите Enter ...'))


@cli.command('ini')
def ini():
    _(""" Создание конфигурационного ini файла """)

    file_exists = False
    for fname in os.listdir('.'):
        if fname.endswith('.ini'):
            file_exists = True

    if file_exists:
        print('\n', _('ini файл уже существует.'))
        input(_('нажмите Enter ...'))
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

        print('\n', _('Файл sap.ini создан'))
        print(_('!!! Заполните все требуемые параметры в файле !!!'))
        input(_('нажмите Enter ...'))


@cli.command('show')
@click.option('-s', required=False, help='_(показать выбранную систему)')
@click.option('-all', is_flag=True, required=False, help='_(показать все системы)')
@click.option('-v', help='_(показать пароли)', is_flag=True)
def show(all, s, v):
    _(""" Информация о SAP системах находящихся в базе данных """)

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
    print('\n')
    input(_('нажмите Enter ...'))


@cli.command('key')
def key():
    _(""" Создание ключей шифрования """)

    Crypto().generate_keys()
    print('\n', _('Ключи шифрования созданы: public_key.txt и private_key.txt'))
    print(_('Необходимо указать их расположение в файле *.ini'))
    print(_('Файл private_key.txt должен находиться в зашифрованном хранилище'))
    input(_('нажмите Enter ...'))


if __name__ == '__main__':
    cli()

# функция перевода через модуль gettext
_ = lambda s: s
