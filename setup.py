#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages
from sap import __version__

setup(
    name='sap',
    version='__version__',
    license='MIT',
    description='Command line tool for launching SAP systems from SAPLogon',

    author='Rygor',
    author_email='pisemco@gmail.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['click', 'SQLAlchemy', 'sqlalchemy_utils', 'cryptography', 'pyperclip', 'prettytable',
                      'six', 'pyzipper', 'rich', 'click_log', 'pyautogui', 'rich_click'],

    entry_points={
        'console_scripts': [
            'sap = sap.cli:sap_cli',
        ]
    },
)
