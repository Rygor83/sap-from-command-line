import configparser
import os
import subprocess
import sys
import click
from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Sap(Base):
    __tablename__ = 'sap'
    system_id = Column(String(3), primary_key=True)
    mandant_num = Column(String(3), primary_key=True)
    user_id = Column(String(10), primary_key=True)
    password = Column(String(55))


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

        if os.path.isfile(f"{os.path.splitext(os.path.basename(__file__))[0]}.ini"):
            path = os.path.join(
                os.path.dirname(__file__),
                f"{os.path.splitext(os.path.basename(__file__))[0]}.ini")
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
def run(system, mandant, u='', p='', l='RU', v=''):
    """ Start SAP system """

    # Считываем конфигурационный файл
    cfg = Config()
    cfg.get_config()

    # Подсоединяемся к базе данных и запрашиваем данные
    db = Database()
    sap_data = db.query(system, mandant, u)

    if v:
        print(sap_data[0])
        answer = input('press Enter to continue or type something to stop: ')
        if answer:
            sys.exit()

    argument = [cfg.config['APPLICATION']['command_line']]

    item = '-system=' + sap_data[0][0].upper()
    argument.append(item)

    item = '-client=' + sap_data[0][1].upper()
    argument.append(item)

    # язык для входа. по умолчанию подставляется RU, если не указано другое.
    item = '-language=' + l
    argument.append(item)

    # можно вводить пользователя самостоятельно отличного от пользователя в БД
    if u:
        item = '-user=' + u
        argument.append(item)
    else:
        item = '-user=' + sap_data[0][2].upper()
        argument.append(item)

    # можно вводить пароль самостоятельно отличный от пароля в БД
    if p:
        item = '-pw=' + p
        argument.append(item)
    else:
        item = '-pw=' + sap_data[0][3]
        argument.append(item)

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
    db.add(system, mandant, user, password)


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
    db.update(system, mandant, user, password)


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

        config['KEYS'] = {'public_key': 'pbk', 'privat_key': 'pvk'}

        print(os.path.basename(__file__))
        with open(f"{os.path.splitext(os.path.basename(__file__))[0]}.ini",
                  'w') as configfile:
            config.write(configfile)

        print('Файл sap.ini создан')
        input('нажмите Enter ...')


@cli.command('show')
@click.option('-s', required=False)
@click.option('-all', is_flag=True, required=False)
def show(all, s):
    """ Show available systems in db """

    if all:
        # Подсоединяемся к базе данных и запрашиваем данные
        db = Database()
        sap_data = db.query()
        for system in sap_data:
            print(system)
        input('нажмите Enter ...')
    elif s:
        # Подсоединяемся к базе данных и запрашиваем данные
        db = Database()
        sap_data = db.query(s)
        for system in sap_data:
            print(system)
        input('нажмите Enter ...')


if __name__ == '__main__':
    cli()
