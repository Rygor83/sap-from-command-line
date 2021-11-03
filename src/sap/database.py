#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
import os
import sys
import click
import sap.utilities as utilities

from sqlalchemy import Column, String, BLOB
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.engine.url import URL
from sqlalchemy_utils import drop_database, database_exists

Base = declarative_base()


class Sap(Base):
    __tablename__ = 'sap'
    system_id = Column(String(3), primary_key=True)
    mandant_num = Column(String(3), primary_key=True)
    user_id = Column(String(10), primary_key=True)
    password = Column(BLOB)
    customer = Column(String(20), primary_key=False)
    description = Column(String(20), primary_key=False)
    url = Column(String(250), primary_key=False)


class Param(Base):
    __tablename__ = 'parameters'
    transaction = Column(String(20), primary_key=True)
    parameter = Column(String(100))


class SapDB():  # noqa : E801
    """ Database processing class  """
    session = ''

    def __init__(self, db_path='', db_type=''):  # type (str) -> ()
        """
        Connect to database.

        :param db_path: Path to database including database name
        :param db_type: Database type: sqlite, Postgresql, mysql, etc.
        """
        self.database_name = 'sap_systems.db'
        self.database_type = db_type if db_type else 'sqlite'
        self.database_path = db_path if db_path else os.path.join(utilities.path(), self.database_name)

        # self.database_url = URL(
        #     self.database_type,
        #     username=credentials['username'],
        #     password=credentials['password'],
        #     host=credentials['host'],
        #     port=credentials['port'],
        #     database=credentials['database'],
        #     query=dict(driver='SQL+Server')
        # )

        self.database_url = f"{self.database_type}:///{self.database_path}"

        if database_exists(self.database_url):
            # Путь по умолчанию
            engine = create_engine(self.database_url)
            session = sessionmaker(bind=engine)
            self.session = session()
        else:
            pass  # raise DatabaseDoesNotExists

    def create(self):
        """
        Database creation
        :return:
        """

        if database_exists(self.database_url):
            raise DatabaseExists(self.database_path)
        else:
            engine = create_engine(self.database_url)
            Base.metadata.create_all(engine)

            session = sessionmaker(bind=engine)
            self.session = session()

            # click.echo(click.style('База данных создана \n', **utilities.color_success))
            # click.echo('Путь: %s \n' % click.format_filename(self.database_path))
            # click.echo(
            #     click.style('!!! Базу данных нужно хранить в защищенном хранилище \n', **utilities.color_sensitive))
            # click.echo(
            #     click.style(f'Путь к базе данных следует указать в {cfg.Config.ini_file} \n',
            #                 **utilities.color_message))
            # click.pause('Нажмите для продолжения ...')

    def add(self, sap_system):  # type (namedtuple) -> list
        """Add a task dict to db."""
        record = Sap(system_id=sap_system.system,
                     mandant_num=sap_system.mandant,
                     user_id=str(sap_system.user).zfill(3),
                     password=sap_system.password,
                     customer=sap_system.customer,
                     description=sap_system.description)
        result = self.session.add(record)
        try:
            self.session.commit()
        except IntegrityError:
            return result
        return result

    def query_system(self, sap_system):
        # TODO: бывает, что ошибаешься, вместо D7H пишешь D7 - нужно делать аля D7*,
        #  чтобы система искала какие системы есть и выводила для выбора

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password, Sap.customer,
                                   Sap.description)
        if sap_system.system:
            query = query.filter_by(system_id=sap_system.system)
        if sap_system.mandant:
            query = query.filter_by(mandant_num=sap_system.mandant)
        if sap_system.user:
            query = query.filter_by(user_id=sap_system.user)
        if sap_system.customer:
            query = query.filter_by(customer=sap_system.customer)
        if sap_system.description:
            query = query.filter_by(description=sap_system.description)
        return query.all()

    def update(self, sap_system):  # type (namedtuple) -> list
        """Modify task in db with given task_id."""
        result = ''

        query = self.session.query(Sap)
        try:
            result = query.filter(Sap.system_id == sap_system.system, Sap.mandant_num == sap_system.mandant,
                                  Sap.user_id == sap_system.user).one()
        except NoResultFound:
            return None

        if result:
            result.password = sap_system.password
            result.customer = sap_system.customer
            result.description = sap_system.description
            self.session.commit()

    def delete(self, sap_system):  # type (namedtuple) -> bool
        """Remove a task from db with given task_id."""
        result = ''

        query = self.session.query(Sap)
        try:
            result = query.filter(Sap.system_id == sap_system.system, Sap.mandant_num == sap_system.mandant,
                                  Sap.user_id == sap_system.user).one()
        except NoResultFound:
            return result

        self.session.delete(result)
        self.session.commit()

        return result

    def query_param(self, transaction):
        """Remove all tasks from db."""
        query = self.session.query(Param.transaction, Param.parameter)
        if transaction:
            query = query.filter_by(transaction=transaction)
        return query.all()

    def drop(self):
        """ Dropping datase"""
        drop_database(self.database_url)

    def stop_sap_db(self):
        """Disconnect from DB."""
        self.session.close()

    # \/\/\/\/\/\/\/\/\/\/\/\/\/ TO DELETE METHODS \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

    def run(self, sap_system):  # # type (namedtuple) -> list
        """ Запуск указанной SAP системы \n Обязательные параметры: 1. система, 2. мандант (не обязательно)  """

        # TODO: бывает, что ошибаешься, вместо D7H пишешь D7 - нужно делать аля D7*,
        #  чтобы система искала какие системы есть и выводила для выбора

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password, Sap.customer,
                                   Sap.description)
        if sap_system.system:
            query = query.filter_by(system_id=sap_system.system)
        if sap_system.mandant:
            query = query.filter_by(mandant_num=sap_system.mandant)
        if sap_system.user:
            query = query.filter_by(user_id=sap_system.user)
        return query.all()

    def list_systems(self, system):  # type (str) -> list[dict]
        """Return list of tasks."""

        # TODO: Сделать Fuzzy search если пользователь ошибся

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password, Sap.customer,
                                   Sap.description)
        if system:
            query = query.filter_by(system_id=system)
        return query.all()

    def pw(self, sap_system):  # # type (namedtuple) -> bool
        """Return number of tasks in db."""

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password, Sap.customer,
                                   Sap.description)
        if sap_system.system:
            query = query.filter_by(system_id=sap_system.system)
        if sap_system.mandant:
            query = query.filter_by(mandant_num=sap_system.mandant)

        return query.all()

    # ^^^^^^^^^^^^^^^^^^^^^ TO DELETE METHODS ^^^^^^^^^^^^^^^^^^^^^


def start_sap_db(db_path, db_type):
    """Connect to db."""
    return SapDB(db_path, db_type)


class DatabaseExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, db_path, message="Database alrady exists"):
        self.message = f"{message}. Path: {db_path}"
        super().__init__(self.message)


class DatabaseDoesNotExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, message="Database does not exist"):
        self.message = message
        super().__init__(self.message)
