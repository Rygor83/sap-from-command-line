#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='sap',
    version='3.2.0',
    license='MIT',
    description='Command line tool for launching SAP systems from SAPLogon',

    author='Rygor',
    author_email='pisemco@gmail.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    ## https://setuptools.pypa.io/en/latest/userguide/datafiles.html
    # package_data={'sap': ['*.ini']},

    install_requires=['click', 'SQLAlchemy', 'sqlalchemy_utils', 'cryptography', 'pyperclip', 'prettytable',
                      'six', 'pyzipper', 'rich', 'click_log', 'pyautogui', 'rich_click'],

    entry_points={
        'console_scripts': [
            'sap = sap.cli:sap_cli',
        ]
    },
)
