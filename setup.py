#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='sap',
    version='3.0',  # Версию нужно править и в __init__.py
    license='MIT',
    description='SAP launcher from command line',

    author='Rygor',
    author_email='pisemco@gmail.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['click', 'SQLAlchemy', 'sqlalchemy_utils', 'cryptography', 'pyperclip', 'prettytable',
                      'six', 'pyzipper', 'rich'],

    entry_points={
        'console_scripts': [
            'sap = sap.cli:sap_cli',
        ]
    },
)
