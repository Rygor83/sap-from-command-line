#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
import os
import click

from sqlalchemy import Column, String, BLOB
from sqlalchemy import create_engine, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.engine.url import URL
from sqlalchemy_utils import drop_database, database_exists

import sap.utilities as utilities
from sap.file_names import DATABASE_NAME
from sap.exceptions import DatabaseDoesNotExists
from sap.exceptions import DatabaseExists, DatabaseDoesNotExists

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

    def __init__(self, db_path: str = '', db_type: str = ''):  # type (str) -> ()
        """
        Connect to database.

        :param db_path: Path to database including database name
        :param db_type: Database type: sqlite, Postgresql, mysql, etc.
        """
        self.database_name = DATABASE_NAME
        self.database_type = db_type if db_type else 'sqlite'
        self.database_path = db_path if db_path else os.path.join(utilities.path(), self.database_name)

        db_credentials = {'username': None,
                          'password': None,
                          'host': None,
                          'database': str(self.database_path),
                          'port': None}

        self.database_url = URL.create(
            drivername=self.database_type,
            username=db_credentials['username'],
            password=db_credentials['password'],
            host=db_credentials['host'],
            port=db_credentials['port'],
            database=db_credentials['database'],
        )

    def make_session(self):
        if database_exists(self.database_url):
            # Путь по умолчанию
            engine = create_engine(self.database_url)
            session = sessionmaker(bind=engine)
            self.session = session()
        else:
            raise DatabaseDoesNotExists(self.database_path)

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

    def add(self, sap_system):  # type (namedtuple) -> list
        """Add a task dict to db."""
        record = Sap(system_id=sap_system.system,
                     mandant_num=str(sap_system.mandant).zfill(3),
                     user_id=sap_system.user,
                     password=sap_system.password,
                     customer=sap_system.customer,
                     description=sap_system.description,
                     url=sap_system.url)
        result = self.session.add(record)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return result
        return result

    def query_system(self, sap_system):

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password, Sap.customer,
                                   Sap.description, Sap.url).order_by(asc(Sap.customer), asc(Sap.system_id),
                                                                      asc(Sap.mandant_num), asc(Sap.user_id))
        if sap_system.system:
            query = query.filter(Sap.system_id.ilike(f"%{sap_system.system}%"))
        if sap_system.mandant:
            query = query.filter(Sap.mandant_num.ilike(f"%{sap_system.mandant}%"))
        if sap_system.user:
            query = query.filter(Sap.user_id.ilike(f"%{sap_system.user}%"))
        if sap_system.customer:
            query = query.filter(Sap.customer.ilike(f"%{sap_system.customer}%"))
        if sap_system.description:
            query = query.filter(Sap.description.ilike(f"%{sap_system.description}%"))
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
            result.url = sap_system.url
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


def start_sap_db(db_path, db_type):
    """Connect to db."""
    return SapDB(db_path, db_type)
