from setuptools import setup

setup(
    name='sap',
    version='0.1',
    py_modules=['sap'],
    include_package_data=True,
    install_requires=[
        'click',
        'sqlalchemy',
        'cryptography',
        'prettytable', 'colorama', 'termcolor'
    ],
    entry_points='''[console_scripts]sap=sap:cli''', )
