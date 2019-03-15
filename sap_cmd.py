import click
import os
import subprocess
import sys
import sqlalchemy
from sqlalchemy import Table, Column, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, CheckConstraint, ForeignKeyConstraint
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

engine = create_engine(
    f"sqlite:///{os.path.splitext(os.path.basename(__file__))[0]}.db")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Sap(Base):
    __tablename__ = 'sap'
    system_id = Column(String(3), primary_key=True)
    mandant_num = Column(String(3), primary_key=True)
    user_id = Column(String(10), primary_key=True)
    password = Column(String(55))


class Config(object):
    def __init__(self):
        self.config = {}
        self.config['CONNECTION'] = {}
        self.config['APPLICATION'] = {}
        self.config['KEYS'] = {}

    def get_config(self):


        config = configparser.ConfigParser()

        if os.path.isfile(f"{os.path.splitext(os.path.basename(__file__))[0]}.ini"):
            path = os.path.join(
                os.path.dirname(__file__),
                f"{os.path.splitext(os.path.basename(__file__))[0]}.ini")
        else:
            print('ini file does not exist. To create - run command "ini"')
            input('press Enter')
            sys.exit()

        read = config.read(path)
        if not read:
            print('File with config parameters')
        else:
            self.config['CONNECTION'] = config['CONNECTION']
            self.config['APPLICATION'] = config['APPLICATION']
            self.config['KEYS'] = config['KEYS']


cfg = Config()
cfg.get_config()


@click.group()
# @click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Version of script')
def cli():
    """ SAP command line """


@cli.command('logon')
def logon():
    ''' Starting SAPLogon '''

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

    query = session.query(Sap.system_id, Sap.mandant_num, Sap.user_id,
                          Sap.password)
    if system:
        query = query.filter_by(system_id=system)
    if mandant:
        query = query.filter_by(mandant_num=mandant)
    if u:
        query = query.filter_by(user_id=u)

    sap_data = query.all()
    if v:
        print(sap_data[0])
        exit = input('press Enter to continue or type something to stop: ')
        if exit:
            sys.exit()

    argument = [cfg.config['APPLICATION']['command_line']]

    item = '-system=' + sap_data[0][0].upper()
    argument.append(item)

    item = '-client=' + sap_data[0][1].upper()
    argument.append(item)

    item = '-language=' + 'RU'
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


@cli.command('db')
def database():
    ''' Create database '''

    # check if db exists
    file_exists = False
    for fname in os.listdir('.'):
        if fname.endswith('.db'):
            file_exists = True

    if file_exists:
        print('Database already exists')
        input('press Enter')
    else:
        db_name = f"{os.path.splitext(os.path.basename(__file__))[0]}.db"

        engine = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(engine)
        print('Database', db_name, 'created')
        input('press Enter')


@cli.command('add')
@click.option('-system', prompt=True, help='system id')
@click.option(
    '-mandant', prompt=True, help='mandant num', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='user id')
@click.option(
    '-password',
    help='password',
    prompt=True,
    confirmation_prompt=True
    # , hide_input=True
)
def add(system, mandant, user, password):
    ''' Add SAP system to database '''
    print('\nadding system to db')
    print(system, mandant, user, password)

    # Base = declarative_base()

    sap_info = Sap(
        system_id=system, mandant_num=mandant, user_id=user, password=password)

    session.add(sap_info)
    session.commit()


@cli.command('update')
@click.option('-system', prompt=True, help='system id')
@click.option(
    '-mandant', prompt=True, help='mandant num', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='user id')
@click.option(
    '-password',
    help='password',
    prompt=True,
    confirmation_prompt=True
    # , hide_input=True
)
def update(system, mandant, user, password):
    ''' Update password for system, mandant and user '''

    query = session.query(Sap)
    result = query.filter(Sap.system_id == system, Sap.mandant_num == mandant,
                          Sap.user_id == user).first()
    result.password = password
    session.commit()


@cli.command('delete')
@click.option('-system', prompt=True, help='system id')
@click.option(
    '-mandant', prompt=True, help='mandant num', type=click.IntRange(1, 999))
@click.option('-user', prompt=True, help='user id')
def delete(system, mandant, user):
    ''' Deleting specific system '''

    query = session.query(Sap)
    result = query.filter(Sap.system_id == system, Sap.mandant_num == mandant,
                          Sap.user_id == user).one()
    session.delete(result)
    session.commit()

    del_res = query.first()
    print('del_res', del_res)

    print('\nSystem', system, '-', mandant, 'deleted succesfully for user', user)


@cli.command('ini')
def ini():
    ''' Create ini file '''

    file_exists = False
    for fname in os.listdir('.'):
        if fname.endswith('.ini'):
            file_exists = True

    if file_exists:
        print('ini fule already exists')
        input('press Enter')
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
        input('press Enter')


@cli.command('show')
@click.option('-s', required=False)
@click.option('-all', is_flag=True, required=False)
def show(all, s):
    ''' Show available systems in db '''

    if all:
        sap_data = session.query(Sap.system_id, Sap.mandant_num, Sap.user_id,
                                 Sap.password).all()
        for system in sap_data:
            print(system)
    elif s:
        query = session.query(Sap.system_id, Sap.mandant_num, Sap.user_id,
                              Sap.password)
        query = query.filter_by(system_id=s)
        sap_data = query.all()
        for system in sap_data:
            print(system)


if __name__ == '__main__':
    cli()
