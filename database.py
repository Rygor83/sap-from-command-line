#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import os
import click
import sys
from sqlalchemy import Column, String, BLOB
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import config as cfg

Base = declarative_base()


class Sap(Base):
    __tablename__ = 'sap'
    system_id = Column(String(3), primary_key=True)
    mandant_num = Column(String(3), primary_key=True)
    user_id = Column(String(10), primary_key=True)
    password = Column(BLOB)


class Param(Base):
    __tablename__ = 'parameters'
    transaction = Column(String(20), primary_key=True)
    parameter = Column(String(100))


class Database(object):
    """
    Класс для работы с базой данных
    """

    db_name = 'database.db'

    def __init__(self):

        conf = cfg.Config()
        conf.read()
        path_db = conf.data['DATABASE']['path']
        if os.path.isfile(path_db):
            engine = create_engine(f"sqlite:///{path_db}")
            session = sessionmaker(bind=engine)
            self.session = session()
        else:
            click.echo(click.style('Базы данных не существует. Для создания запустите команду "db"  \n', bg='black',
                                   fg='yellow'))
            click.pause('Нажмите для продолжения ...')
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
                click.echo(click.style('По указанным данным найти ничего не получилось  \n', bg='black',
                                       fg='yellow'))
                click.echo([system, client, user])
                click.pause('Нажмите для продолжения ...')
                sys.exit()

    def query_param(self, trans=''):
        """
        Методе для запросов информации о SAP системе
        :transaction: код транзакции;
        :return: информация о параметре транзакции;
        """

        query = self.session.query(Param.transaction, Param.parameter)
        if trans:
            query = query.filter_by(transaction=trans)

        result = query.all()

        if result:
            return result

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
            click.echo(click.style('Данные уже существуют в базе данных:  \n', bg='black',
                                   fg='yellow'))
            click.echo([system, client, user])
            click.pause('Нажмите для продолжения ...')
            sys.exit()

    def update(self, system, mandant, user, password):
        client = str(mandant).zfill(3)

        result = self.filter(client, system, user)

        if result:
            result.password = password
            self.session.commit()
        else:
            click.echo(click.style('Ничего не найден для удаления по введенным данным: \n', bg='black', fg='yellow'))
            click.echo([system, client, user])
            click.pause('Нажмите для продолжения ...')
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
            click.echo(click.style('Ничего не найден для удаления по введенным данным: \n', bg='black', fg='yellow'))
            click.echo([system, client, user])
            click.pause('Нажмите для продолжения ...')
            sys.exit()
        return result
