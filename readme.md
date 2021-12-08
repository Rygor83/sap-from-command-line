# sap from command line

[![Python 3.9+](docs/resources/images/python-v3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)

[![Windows](docs/resources/images/os-windows-blue.svg)](https://github.com/Rygor83/sap-command-line)

[![GitHub license](docs/resources/images/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

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

### sap start

```
Usage: sap start [OPTIONS]

  Starting point for working wiht SAP command line tool
  1. Database creation.
  2. ini file with config parameters createion.
  3. Usefull messages

Options:
  -h, --help  Show this message and exit.  [default: False]
```

### sap add

```
Usage: sap add [OPTIONS]

  Add sap system with it's parameters to db. Just run 'sap add' and follow
  instructions.

Options:
  -system ONLY LETTERS AND NUMBERS. 3 CHARS LENGTH
                                  System Id
  -mandant INTEGER RANGE          Mandant/Client number  [1<=x<=999]
  -user TEXT                      User
  -password TEXT                  Password
  -customer TEXT                  Customer name
  -description TEXT               SAP system description
  -url TEXT                       SAP system Url
  -v, --verbose                   Show passwords for selected systems
                                  [default: True]
  -h, --help                      Show this message and exit.  [default:
                                  False]
```

### sap run

```
Usage: sap run [OPTIONS] [SYSTEM] [MANDANT]

  Launch SAP system

  Optional arguments:
  1. SYSTEM: Request a SAP system by systedm id
  2. MANDANT: Request a SAP system by mandant/client

Options:
  -u, --user TEXT            Request a SAP system by user
  -c, --customer TEXT        Request a SAP system by customer
  -d, --description TEXT     Request a SAP system by description
  -eu, --external_user       Flag. Launch sap system with external user
                             (outside database)  [default: False]
  -l, --language TEXT        Logon language
  -t, --transaction TEXT     Run transaction
  -s, --system_command TEXT  Run system_command: /n, /o, /i, /nend, /nex,
                             /*<transaction_code>, /n<transaction_code>,
                             /o<transaction_code>, /h
  -r, --report TEXT          Run report
  -p, --parameter TEXT       Transaction's parameters
  -w, --web                  Flag. Launch system's web site  [default: False]
  -r, --reuse                Flag. Defines whether an existing connection to
                             an SAP is reused  [default: True]
  -h, --help                 Show this message and exit.  [default: False]
```

## Configuration

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)