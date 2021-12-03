# sap

[![Python 3.9+](resources/images/python-v3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)

[![Windows](resources/images/os-windows-blue.svg)](https://github.com/Rygor83/sap-command-line)

[![GitHub license](resources/images/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Windows Command line tool for launching SAP systems from SAPlogon for SAP consultant and advanced SAP users.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```cmd
pip install <path to sap package folder>
```

## Start

## Usage

```
Usage: sap [OPTIONS] COMMAND [ARGS]...

  Command line tool to launch SAP systems from SAPLogon

  Run 'sap start' to start working

Options:
  -path, --config_path PATH  Path to external sap_config.ini folder
  --version                  Show the version and exit.  [default: False]
  -h, --help                 Show this message and exit.  [default: False]

Commands:
  about     Display 'About SAP logon' window
  add       Add sap system with it's parameters to db.
  backup    Create backup
  config    Config file creation or editing
  db        Database creation.
  debug     System debug: either create debug file or start system debuggin
  delete    Delete requested record about SAP system from database
  keys      Encryption keys creation.
  list      Print information about SAP systems
  logon     Launch SAPLogon application
  pw        Copy password for the requested system into clipboard.
  run       Launch SAP system
  shortcut  Display 'SAP GUI Shortcut' window
  start     Starting point for working wiht SAP command line tool
  stat      Displays 'System: status' window
  update    Update record from database
```

## Configuration

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)