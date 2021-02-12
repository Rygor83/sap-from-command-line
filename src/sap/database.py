#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
import os

from sqlalchemy import Column, String, BLOB
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

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


class SapDB():  # noqa : E801
    """Wrapper class for TinyDB.

    The methods in this class need to match
    all database interaction classes.

    So far, this is:
    TasksDB_MongoDB found in tasksdb_pymongo.py.
    TasksDB_TinyDB found in tasksdb_tinydb.py.
    """
    session = ''

    def __init__(self, db_path, db_type):  # type (str) -> ()
        """Connect to db."""
        if os.path.exists(db_path):
            engine = create_engine(f"{db_type}:///{db_path}")
            session = sessionmaker(bind=engine)
            self.session = session()
        else:
            engine = create_engine(f"sqlite:///{self.db_name}")
            Base.metadata.create_all(engine)

            session = sessionmaker(bind=engine)
            self.session = session()

            click.echo(click.style('База данных создана \n', bg='black', fg='green'))
            click.echo('Путь: %s \n' % click.format_filename(self.db_name))
            click.echo(click.style('!!! Базу данных нужно хранить в защищенном хранилище \n', bg='red', fg='white'))
            click.echo(
                click.style(f'Путь к базе данных следует указать в {cfg.Config.ini_file} \n', bg='black', fg='white'))
            click.pause('Нажмите для продолжения ...')

    def create(db_path, db_type):
        if os.path.exist():  # self.exists():
            click.echo(click.style('Базы данных существует. \n', bg='black', fg='yellow'))
            click.pause('Нажмите для продолжения ...')
            sys.exit()
        else:
            engine = create_engine(f"sqlite:///{self.db_name}")
            Base.metadata.create_all(engine)

            click.echo(click.style('База данных создана \n', bg='black', fg='green'))
            click.echo('Путь: %s \n' % click.format_filename(self.db_name))
            click.echo(click.style('!!! Базу данных нужно хранить в защищенном хранилище \n', bg='red', fg='white'))
            click.echo(
                click.style(f'Путь к базе данных следует указать в {cfg.Config.ini_file} \n', bg='black', fg='white'))
            click.pause('Нажмите для продолжения ...')

    def add(self, sap_system):  # type (namedtuple) -> list
        """Add a task dict to db."""
        record = Sap(system_id=sap_system.system,
                     mandant_num=sap_system.mandant,
                     user_id=str(sap_system.user).zfill(3),
                     password=sap_system.password)
        result = self.session.add(record)
        try:
            self.session.commit()
        except IntegrityError:
            pass
        return result

    def run(self, sap_system):  # # type (namedtuple) -> list
        """Return a task dict with matching id."""
        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password)
        if sap_system.system:
            query = query.filter_by(system_id=sap_system.system)
        if sap_system.mandant:
            query = query.filter_by(mandant_num=sap_system.mandant)
        if sap_system.user:
            query = query.filter_by(user_id=sap_system.user)
        return query.all()

    def list_systems(self, system):  # type (str) -> list[dict]
        """Return list of tasks."""

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password)
        if system:
            query = query.filter_by(system_id=system)
        return query.all()

    def pw(self, sap_system):  # # type (namedtuple) -> bool
        """Return number of tasks in db."""

        query = self.session.query(Sap.system_id, Sap.mandant_num, Sap.user_id, Sap.password)
        if sap_system.system:
            query = query.filter_by(system_id=sap_system.system)
        if sap_system.mandant:
            query = query.filter_by(mandant_num=sap_system.mandant)

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

    def stop_sap_db(self):
        """Disconnect from DB."""
        self.session.close()


def start_sap_db(db_path, db_type):  # type (str) -> TasksDB_MongoDB object
    """Connect to db."""
    return SapDB(db_path, db_type)
