import click


@click.group()
@click.version_option()
def cli():
	""" SAP command line """


@cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False)
@click.option('-u', help='user id')
@click.option('-p', help='password')
@click.option('-l', help='language', default='RU')
@click.option('-v', help='verbose', is_flag=True)
def run(system, mandant, u='', p='', l = 'RU', v=''):
	""" start SAP system """
	print(system, mandant, u, p, l, v)


@cli.command('db')
def database():
	''' create database '''
	print('create database')
	
	
@cli.command('add')
def add():
	''' add SAP system to database '''
	print('adding system to db')
	
	
@cli.command('ini')
def ini():
	''' create ini file '''
	print('creating ini file')
	
	
@cli.command('show')
@click.option('-s')
@click.option('-all', is_flag=True)
def show(all, s):
	''' show available systems in db '''
	if all:
		print('showing all systems')
	else:
		print('showing only system', s)


if __name__ == '__main__':
	cli()

