import click


def print_version(ctx, param, value):
	if not value or ctx.resilient_parsing:
		return click.echo('Version 1.0 \n')
	ctx.exit()


@click.group()
# @click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Version of script')
def cli():
	""" SAP command line """


@cli.command('run')
@click.argument('system')
@click.argument('mandant', required=False, type=click.IntRange(1,999))
@click.option('-u', help='user id')
@click.option('-p', help='password')
@click.option('-l', help='language', default='RU')
@click.option('-v', help='verbose', is_flag=True)
def run(system, mandant, u='', p='', l='RU', v=''):
	""" start SAP system """
	print(system, mandant, u, p, l, v)


@cli.command('db')
def database():
	''' Create database '''
	print('create database')


@cli.command('add')
def add():
	''' Add SAP system to database '''
	print('adding system to db')


@cli.command('ini')
def ini():
	''' Create ini file '''
	print('creating ini file')


@cli.command('show')
@click.option('-s')
@click.option('-all', is_flag=True)
def show(all, s):
	''' Show available systems in db '''
	if all:
		print('showing all systems')
	else:
		print('showing only system', s)


if __name__ == '__main__':
	cli()

