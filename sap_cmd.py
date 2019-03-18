import configparser
import os
import subprocess
import sys
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
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            print('Базы данных не существует. Для создания запустите команду "db" ')
            input('нажмите Enter')
            sys.exit()

    def query(self, system='', mandant='', user=''):

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password)
        if system:
            query = query.filter_by(system_id=system)
        if mandant:
            query = query.filter_by(mandant_num=mandant)
        if user:
            query = query.filter_by(user_id=user)

        return query.all()

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
        self.config = {'CONNECTION': {}, 'APPLICATION': {}, 'KEYS': {}}

    def get_config(self):

        ini_file = f"{os.path.splitext(os.path.basename(__file__))[0]}.ini"
        if os.path.isfile(ini_file) and os.stat(ini_file).st_size != 0:
            path = os.path.join(os.path.dirname(__file__), ini_file)
        else:
            print('ini файла не существует. Для создания запустите команду "ini" ')
            input('нажмите Enter')
            sys.exit()

        config = configparser.ConfigParser()

        read = config.read(path)
        if not read:
            print('File with config parameters')
        else:
            self.config['CONNECTION'] = config['CONNECTION']
            self.config['APPLICATION'] = config['APPLICATION']
            self.config['KEYS'] = config['KEYS']


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
            print("Ключи шифрования созданы.")
            input("нажмите Enter")
        else:
            print("Ключи шифрования уже созданы")
            input("нажмите Enter ...")

    @staticmethod
    def encrypto(password):
        cfg = Config()
        cfg.get_config()
        with open(cfg.config['KEYS']['public_key'], "rb") as key_file:
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
        with open(cfg.config['KEYS']['private_key'], "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())

        decrypted_data = private_key.decrypt(encrypted_password,
                                             padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None)).decode()
        return decrypted_data


@click.group()
def cli():
    """ SAP command line """


@cli.command('logon')
def logon():
    """ Starting SAPLogon """

    # Считываем конфигурационный файл
    cfg = Config()
    cfg.get_config()

    # Запускаем saplogon.exe
    click.launch(cfg.config['APPLICATION']['sap'])


@cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1, 999))
@click.option('-u', help='user id')
@click.option('-p', help='password')
@click.option('-l', help='language', default='RU')
@click.option('-v', help='verbose', is_flag=True)
@click.option('-t', help='transaction code')
def run(system, mandant, u='', p='', l='RU', v='', t=''):
    """ Start SAP system """

    # Считываем конфигурационный файл
    cfg = Config()
    cfg.get_config()

    # Подсоединяемся к базе данных и запрашиваем данные
    db = Database()
    sap_data = db.query(system, mandant, u)

    if len(sap_data) >= 2:
        i = 0
        message = ''
        for item in sap_data:
            i += 1
            message += f"{str(i)}. {item[0]}-{item[1]}: {item[2]} \n"
        print('Выбраны следующие пользователи: ')
        print(message)
        print(f"Выберите пользователя под которым хотим войти в систему.")
        ans = input(f"Допустимый ввод - индекс от 1 до {str(len(sap_data))}: ")
        while not ans.isdigit() or int(ans) > len(sap_data) or int(ans) < 1:
            print(f"\nВозможно вводить значения только от 1 до {str(len(sap_data))}.")
            ans = input(f"Выберите пользователя под которым хотим войти в систему: ")
        ans = int(ans) - 1
    else:
        ans = 0

    if v:
        print('Система:\t', sap_data[ans][0])
        print('Мандант:\t', sap_data[ans][1])
        print('Пользователь:\t', sap_data[ans][2])
        print('Пароль:\t', Crypto.decrypto(sap_data[ans][3]))
        answer = input('press Enter to continue or type something to stop: ')
        if answer:
            sys.exit()

    # Добавляем путь к командному файлу
    argument = [cfg.config['APPLICATION']['command_line']]

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
        input('нажмите Enter ...')


@cli.command('db')
def database():
    """ Create database """

    # check if db exists
    file_exists = False
    for fname in os.listdir('.'):
        if fname.endswith('.db'):
            file_exists = True

    if file_exists:
        print('База данных уже существует.')
        input('нажмите Enter ...')
    else:
        db_name = f"{os.path.splitext(os.path.basename(__file__))[0]}.db"

        eng = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(eng)
        print('База данных', db_name, 'создана.')
        input('нажмите Enter ...')


@cli.command('add')
@click.option('-system', prompt=True, help='system id')
@click.option(
    '-mandant', prompt=True, help='mandant num', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='user id')
@click.option(
    '-password',
    help='password',
    prompt=True,
    confirmation_prompt=True,
    hide_input=True
)
def add(system, mandant, user, password):
    """ Add SAP system to database """
    print('\nadding system to db')
    print(system, mandant, user, password)

    db = Database()
    db.add(system, mandant, user, Crypto.encrypto(str.encode(password)))


@cli.command('update')
@click.option('-system', prompt=True, help='system id')
@click.option(
    '-mandant', prompt=True, help='mandant num', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='user id')
@click.option(
    '-password',
    help='password',
    prompt=True,
    confirmation_prompt=True,
    hide_input=True
)
def update(system, mandant, user, password):
    """ Update password for system, mandant and user """

    db = Database()
    db.update(system, mandant, user, Crypto.encrypto(str.encode(password)))


@cli.command('delete')
@click.option('-system', prompt=True, help='system id')
@click.option(
    '-mandant', prompt=True, help='mandant num', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='user id')
def delete(system, mandant, user):
    """ Deleting specific system """

    db = Database()
    db.delete(system, mandant, user)


@cli.command('ini')
def ini():
    """ Create ini file """

    file_exists = False
    for fname in os.listdir('.'):
        if fname.endswith('.ini'):
            file_exists = True

    if file_exists:
        print('ini файл уже существует.')
        input('нажмите Enter ...')
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

        config['APPLICATION'] = {'command_line': 'cmd', 'sap': 'sap'}

        config['KEYS'] = {'public_key': 'pbk', 'private_key': 'pvk'}

        print(os.path.basename(__file__))
        with open(f"{os.path.splitext(os.path.basename(__file__))[0]}.ini",
                  'w') as configfile:
            config.write(configfile)

        print('Файл sap.ini создан')
        input('нажмите Enter ...')


@cli.command('show')
@click.option('-s', required=False, help='Показать выбранную систему')
@click.option('-all', is_flag=True, required=False, help='показать все системы')
@click.option('-v', help='показать пароль', is_flag=True)
def show(all, s, v):
    """ Show available systems in db """

    if all:
        # Подсоединяемся к базе данных и запрашиваем данные по всем системам
        db = Database()
        sap_data = db.query()
    elif s:
        # Подсоединяемся к базе данных и запрашиваем данные по выбранной системе
        db = Database()
        sap_data = db.query(s)

    for system in sap_data:
        print('Система:\t', system[0])
        print('Мандант:\t', system[1])
        print('Пользователь:\t', system[2])
        if v:
            print('Пароль:\t', Crypto.decrypto(system[3]))
        print('\n')
    input('нажмите Enter ...')


@cli.command('key')
def key():
    """ Создание ключей шифрования """

    Crypto().generate_keys()


if __name__ == '__main__':
    cli()
