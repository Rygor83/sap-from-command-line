import click
import os
import sqlalchemy
from sqlalchemy import Table, Column, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, CheckConstraint, ForeignKeyConstraint
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///sap_info.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Sap(Base):
	__tablename__ = 'sap'
	system_id = Column(String(3), primary_key=True)
	mandant_num = Column(String(3), primary_key=True)
	user_id = Column(String(10), primary_key=True)
	password = Column(String(55))


@click.group()
# @click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Version of script')
def cli():
	""" SAP command line """


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
	print(sap_data)


@cli.command('db')
@click.argument('db_name', default='sap_info')
def database(db_name):
	''' Create database '''

	# check if db exists
	file_exists = False
	for fname in os.listdir('.'):
		if fname.endswith('.db'):
			file_exists = True

	if file_exists:
		print('Database already exists')
	else:
		engine = create_engine(f"sqlite:///{db_name}.db")
		Base.metadata.create_all(engine)
		print('Database', db_name, 'created')


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
	#, hide_input=True
)
def add(system, mandant, user, password):
	''' Add SAP system to database '''
	print('\nadding system to db')
	print(system, mandant, user, password)

	Base = declarative_base()

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
	#, hide_input=True
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
	
	print('\nSystem', system, '-', mandant, 'deleted succesfully for user', user)


@cli.command('ini')
def ini():
	''' Create ini file '''
	print('creating ini file')


@cli.command('show')
@click.option('-s', required=False)
@click.option('-all', is_flag=True, required=False)
def show(all, s):
	''' Show available systems in db '''
	if all:
		sap_data = session.query(Sap.system_id, Sap.mandant_num, Sap.user_id,
																											Sap.password).all()
		for item in sap_data:
			print(item)
	elif s:
		query = session.query(Sap.system_id, Sap.mandant_num, Sap.user_id,
																								Sap.password)
		query = query.filter_by(system_id=s)
		sap_data = query.all()
		for item in sap_data:
			print(item)


if __name__ == '__main__':
	cli()

