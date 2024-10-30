#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Database API """

from pathlib import Path

from sqlalchemy import Column, String, BLOB
from sqlalchemy import create_engine, asc
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy_utils import drop_database, database_exists

import sap.utilities as utilities
from sap.api import DATABASE_NAME
from sap.exceptions import DatabaseExists, DatabaseDoesNotExists

Base = declarative_base()


class Sap(Base):
    """ Table to store information about sap systems """
    __tablename__ = 'sap'
    system_id = Column(String(3), primary_key=True)
    mandant_num = Column(String(3), primary_key=True)
    user_id = Column(String(10), primary_key=True)
    password = Column(BLOB)
    customer = Column(String(20))
    description = Column(String(20))
    url = Column(String(250))
    only_web = Column(String(1))
    autotype = Column(String(250))


class Param(Base):
    """ Table to store transactions and screen-field for them """
    __tablename__ = 'parameters'
    transaction = Column(String(20), primary_key=True)
    parameter = Column(String(100))


# noinspection PyUnresolvedReferences
class SapDB():
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
        self.database_path = Path(db_path) if db_path else Path(utilities.path() / self.database_name)

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
        """ create session """
        if database_exists(self.database_url):
            # Путь по умолчанию
            self.engine = create_engine(self.database_url)
            session = sessionmaker(bind=self.engine)
            self.session = session()

        else:
            raise DatabaseDoesNotExists(self.database_path)

    def create(self):
        """ Database creation """

        if database_exists(self.database_url):
            raise DatabaseExists(self.database_path)
        else:
            engine = create_engine(self.database_url)
            Base.metadata.create_all(engine)

            session = sessionmaker(bind=engine)
            self.session = session()

    def add(self, sap_system):  # type (namedtuple) -> list
        """Add a system to database """
        record = Sap(system_id=sap_system.system,
                     mandant_num=str(sap_system.mandant).zfill(3),
                     user_id=sap_system.user,
                     password=sap_system.password,
                     customer=sap_system.customer,
                     description=sap_system.description,
                     url=sap_system.url,
                     autotype=sap_system.autotype,
                     only_web=sap_system.only_web)
        result = self.session.add(record)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return result
        return result

    def query_system(self, sap_system):
        """ Query system from database """

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password, Sap.customer,
                                   Sap.description, Sap.url, Sap.autotype, Sap.only_web).order_by(asc(Sap.customer),
                                                                                    asc(Sap.system_id),
                                                                                    asc(Sap.mandant_num),
                                                                                    asc(Sap.user_id))
        if sap_system.system:
            # noinspection PyUnresolvedReferences
            query = query.filter(Sap.system_id.ilike(f"%{sap_system.system}%"))
        if sap_system.mandant:
            query = query.filter(Sap.mandant_num.ilike(f"%{sap_system.mandant}%"))
        if sap_system.user:
            query = query.filter(Sap.user_id.ilike(f"%{sap_system.user}%"))
        if sap_system.customer:
            query = query.filter(Sap.customer.ilike(f"%{sap_system.customer}%"))
        if sap_system.description:
            query = query.filter(Sap.description.ilike(f"%{sap_system.description}%"))
        if sap_system.only_web:
            query = query.filter(Sap.only_web.ilike(f"%{sap_system.only_web}%"))
        return query.all()

    def update(self, sap_system):  # type (namedtuple) -> list
        """ Update system in database """
        result = ''

        query = self.session.query(Sap)
        try:
            # noinspection PyUnresolvedReferences
            result = query.filter(Sap.system_id == sap_system.system, Sap.mandant_num == sap_system.mandant,
                                  Sap.user_id == sap_system.user).one()
        except NoResultFound:
            return None

        if result:
            result.password = sap_system.password
            result.customer = sap_system.customer
            result.description = sap_system.description
            result.url = sap_system.url
            result.autotype = sap_system.autotype
            result.only_web = sap_system.only_web
            self.session.commit()

    def delete(self, sap_system):  # type (namedtuple) -> bool
        """ Remove system from database """
        result = ''

        query = self.session.query(Sap)
        try:
            # noinspection PyUnresolvedReferences
            result = query.filter(Sap.system_id == sap_system.system, Sap.mandant_num == sap_system.mandant,
                                  Sap.user_id == sap_system.user).one()
        except NoResultFound:
            return result

        self.session.delete(result)
        self.session.commit()

        return result

    def query_param(self, parameter):
        """List all transactions and it's parameters"""
        query = self.session.query(Param.transaction, Param.parameter)
        if parameter.transaction:
            query = query.filter(Param.transaction.ilike(f"%{parameter.transaction}%"))
        return query.all()

    def delete_param(self, parameter):
        """Delete transactions and it's parameters"""
        result = ''

        query = self.session.query(Param)
        try:
            # noinspection PyUnresolvedReferences
            result = query.filter(Param.transaction == parameter.transaction).one()
        except NoResultFound:
            return result

        self.session.delete(result)
        self.session.commit()

        return result

    def add_param(self, parameter):  # type (namedtuple) -> list
        """Add transaction and its parameters to database """
        record = Param(transaction=parameter.transaction,
                       parameter=parameter.parameter)

        result = self.session.add(record)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return result
        return result

    def update_param(self, parameter):  # type (namedtuple) -> list
        """ Update transaction and its parameters """
        result = ''

        query = self.session.query(Param)
        try:
            # noinspection PyUnresolvedReferences
            result = query.filter(Param.transaction == parameter.transaction).one()
        except NoResultFound:
            return None

        if result:
            result.transaction = parameter.transaction
            result.parameter = parameter.parameter
            self.session.commit()

    def drop(self):
        """ Dropping database"""
        drop_database(self.database_url)

    def stop_sap_db(self):
        """Disconnect from DB."""
        self.session.close_all()


def start_sap_db(db_path, db_type):
    """Connect to db."""
    return SapDB(db_path, db_type)
