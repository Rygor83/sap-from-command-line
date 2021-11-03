#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='sap',
    version='0.2',  # Версию нужно править и в __init__.py
    license='MIT',
    description='Launch sap systems from saplogon with sapshcut.exe',

    author='Rygor',
    author_email='pisemco@gmail.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['click', 'SQLAlchemy', 'sqlalchemy_utils', 'cryptography', 'pyperclip', 'prettytable', 'appdirs',
                      'six'],

    entry_points={
        'console_scripts': [
            'sap = sap.cli:sap_cli',
        ]
    },
)
