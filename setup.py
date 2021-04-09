#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='sap',
    version='0.1.5',
    license='proprietary',
    description='Launch sap systems from saplogon with sapshcut.exe',

    author='Rygor',
    author_email='pisemco@gmail.com',
    url='http://rygor.by',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['click', 'SQLAlchemy', 'cryptography', 'pyperclip', 'prettytable', 'appdirs', 'six'],

    entry_points={
        'console_scripts': [
            'sap = sap.cli:sap_cli',
        ]
    },
)
