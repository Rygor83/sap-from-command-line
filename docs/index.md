# sap

[![Python 3.9+](resources/images/python-v3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)   [![Windows](resources/images/os-windows-blue.svg)](https://github.com/Rygor83/sap-command-line)   [![GitHub license](resources/images/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Windows Command line tool for launching SAP systems from SAPlogon for SAP consultant and advanced SAP users.

## Possibilities:

Like all SAP consultants, I work with different clients in different systems. Each system has its own security levels.
Some customers require changing the password every 3 months, some - once a month. You can remember passwords for those
systems in which you work all the time, but what to do with customers who contact you once every 2-3 months. And
besides, trying to synchronize all passwords to all sap systems is unsafe, and a waste of time.

A long time ago, I wanted to create a database where I could securely store all data about systems, as well as
passwords. And launch systems from the command line. This is how this instrument was born.

What this tool can do:

1. Launch SAP systems from the command line. This is possible with the built-in SAP tool "sapshcut.exe". A detailed
   description of this tool can be found in note [103019](https://launchpad.support.sap.com/#/notes/103019) (local pdf
   version
   is [here](https://github.com/Rygor83/sap-from-command-line/blob/master/Note%20103019_SAP_Command_lines__v57.pdf)). I
   just took this tool and adapted the commands.
2. All system data (System ID, client, user, password, system description, customer name) are stored in a database, the
   password is encrypted with [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)).
3. You can also store the URL if SAP system can be launched in a web browser, as well as an autotype sequence to
   automatically fill in the username and password in the web version of the system.
4. Ability to launch a transaction at sap system startup, as well as transferring the parameters of this transaction.
   For example, you run tr. SE11 and say open table T001. The data for this is also maintained in the database.
5. Launch sap system with user/password not in database so-called external user.
6. Start SAP with additional commands:
    1. transaction (SE37, FB03, etc)
    2. system command (like, /n, /nend, /nex, /o)
    3. reports (tr. SE38 -> report name)
    4. etc
7. Copy a password for the requested system into the clipboard.
8. Creating a password-protected backup with tool's files: configuration file, database, public and private encryption
   keys + XML file with a sap system list in SAPLogon

# Installation

1. Install [Python](https://www.python.org/downloads/). Use version 3.9 and above.
2. Downloaded the latest version from [Releases page](https://github.com/Rygor83/sap-from-command-line/releases) and
   extract it.
3. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install:

```cmd
pip install <path to sap package folder>
``` 

4. Download a tool to create and mount an encrypted virtual drive. We will use it to keep safe a private encryption key.
   For example, [Bestcrypt](https://www.jetico.com).

# Prerequisites

All systems have to be entered into SAPLogon application: description, application server, instance number, system id,
etc).

# Usage

The commands are described below as they are used: which one to start with and which one to use next

## help (-h, --help)

If you need any help about application or commands - just type -h/--help and you'll get the list of all possible
commands.

```cmd
sap -h
```

You will get:

1. List of possible commands
2. List of options

```
Usage: sap [OPTIONS] COMMAND [ARGS]...

  Command line tool to launch SAP systems from SAPLogon

  Run 'sap start' to start working

Options:
  --config_path  -path  PATH  Path to external sap_config.ini folder                                                                                     │
  --version                   Show the version and exit.                                                                                                 │
  --log_level    -l     LVL   Logging. Values: Either CRITICAL, ERROR, WARNING, INFO or DEBUG                                                                             │
  --help         -h           Show this message and exit.

Commands:
  about          Display 'About SAP logon' window                                                                                                        │
  add            Add sap system with it's parameters to db. Just run 'sap add' and follow instructions.                                                  │
  backup         Create backup                                                                                                                           │
  config         Config file creation or editing                                                                                                         │
  db             Database creation. This command is used for technical purpose. Better run 'sap start' command.                                          │
  debug          System debug: either create debug file or start system debuggin                                                                         │
  delete         Delete requested record about SAP system from database                                                                                  │
  keys           Encryption keys creation. This command is used for technical purpose. Better run 'sap start' command.                                   │
  list           Print information about SAP systems                                                                                                     │
  logon          Launch SAPLogon application                                                                                                             │
  paradd         Add transaction's parameter to databse 'Parameters'                                                                                     │
  pardel         Delete transaction's parameter from databse 'Parameters'                                                                                │
  parlist        List transaction's parameter from databse 'Parameters'                                                                                  │
  parupdate      Update record from database                                                                                                             │
  pw             Copy password for the requested system into clipboard. Script waits 10 seconds and clears clipboard.                                                                                           │
  run            Launch SAP system                                                                                                                       │
  shortcut       Display 'SAP GUI Shortcut' window                                                                                                       │
  start          Starting point for working wiht SAP command line tool                                                                                   │
  stat           Displays 'System: status' window                                                                                                        │
  update         Update record from database
```

If you want to get help about specific command, let's say, about command 'add' - type the following command

```cmd
sap add -h
```

You will get:

1. command description
2. command's options, option's types, option's default values

```
Usage: sap add [OPTIONS]

 Add sap system with it's parameters to db. Just run 'sap add' and follow instructions.

Options 
             -system       ONLY LETTERS AND NUMBERS. 3 CHARS LENGTH  System Id                                        
             -mandant      INTEGER RANGE [1<=x<=999]                 Mandant/Client number                            
             -user         TEXT                                      User                                             
             -password     TEXT                                      Password                                         
             -customer     TEXT                                      Customer name                                    
             -description  TEXT                                      SAP system description                           
             -url          TEXT                                      SAP system Url                                   
 --autotype  -a            TEXT                                      Autotype sequence for logining to web site       
                                                                     [default: {USER}{TAB}{PASS}{ENTER}]              
 --verbose   -v                                                      Show passwords for selected systems              
 --help      -h                                                      Show this message and exit.                      
```

## sap start

Starting point for working with SAP command line tool.
Type the following command and follow the instructions.

```cmd
sap start
```

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                   Preparatory work                                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

                                                     Created files:

 1 sap_config.ini - used to store information about all following files locations. Default location is "C:
   \Users<USERNAME>\AppData\Local\sap" folder. Also contains some additional parameters. All parameters have
   description.
 2 public_key.txt - used to encrypt passwords in database. Can be stored in any place. If you move it from default
   location then don't forget to put new place in sap_config.ini -> '[KEYS]' -> 'public_key_path'
 3 private_key.txt - used to decrypt passwords. Must be stored in a secure place. For example, in Bestcrypt container.
   Don't forget to put new place in sap_config.ini -> '[KEYS]' -> 'private_key_path'
 4 database.db - used to store all information about SAP systems. Must be stored in secure place. For example, in
   Bestcrypt container. Don't forget to put new place in sap_config.ini -> '[DATABASE]' -> ' db_path'


                                                      Extra work:

 5 Find 'SAPSHCUT.EXE' file and put its location in sap_config.ini -> '[APPLICATION]' -> 'command_line_path'
 6 Find 'SAPLOGON.EXE' file and put its location in sap_config.ini -> '[APPLICATION]' -> 'saplogon_path'
 7 By default, this key: sap_config.ini -> '[LOCALE]' -> 'language' - have value of windows' default language. This key
   is used as sap logon language. So if you have sap logon language other than windows language - change it.

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                    Start working                                                     ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
To start work with SAP commands after preparatory work:

 • type 'SAP ADD' to add sap system into database
 • type 'SAP RUN <system id> <mandant num>' to launch sap system
 • type 'SAP --HELP' to learn more about program

Press enter to open files folder and start working. Good luck.
```

Now you are ready to work.

## sap add

Now you are ready to add systems to database. Type the following command

```cmd
sap add
```

The following data will be requested (listed below) and after the input, information about the success of the input will
be displayed. The password information will also be displayed and therefore the system will report that the user has 10
seconds for verification and the data will be cleared from the screen.

```
System: XXX
Mandant: 100
User: USER
Password: any password
Repeat for confirmation: any password
Customer []: Customer
Description []: Dev
Url []:
Autotype [{USER}{TAB}{PASS}{ENTER}]:


                               The following system is ADDED to the database:
┌─────────────────────┬────────────────┬──────────────────┬──────────────────────────┬────────────┬────────────────────┐
│ Customer            │ System         │ Mandant          │ Description              │ User       │ Password           │
╞═════════════════════╪════════════════╪══════════════════╪══════════════════════════╪════════════╪════════════════════╡
│ BESTCUSTOMER        │ XXX            │ 100              │ Dev                      │ USER       │ 1234               │
└─────────────────────┴────────────────┴──────────────────┴──────────────────────────┴────────────┴────────────────────┘
Information about passwords will be deleted from screen in 10:

```

Try to add yourself the following information into database with 'sap add' command

```
System: YYY
Mandant: 200
User: XXX
Password: any password
Repeat for confirmation: any password
Customer []: BESTCUSTOMER
Description []: Test
Url []: www.sap.com
Autotype [{USER}{TAB}{PASS}{ENTER}]:
```

## sap list

1. If you want to see information about all systems the type the following command

```cmd
sap list
```

```
                                              Available systems
┌─────────────────────────┬──────────────┬────────────────┬──────────────────────────┬─────────────────────────────────┐
│ Customer                │ System       │ Mandant        │ Description              │ User                            │
╞═════════════════════════╪══════════════╪════════════════╪══════════════════════════╪═════════════════════════════════╡
│ BESTCUSTOMER            │ XXX          │ 100            │ Dev                      │ XXX                             │
│ BESTCUSTOMER            │ YYY          │ 200            │ Test                     │ XXX                             │
└─────────────────────────┴──────────────┴────────────────┴──────────────────────────┴─────────────────────────────────┘
```

2. If you need information about specific system/mandant then type 'sap list system mandant'

```cmd
sap list xxx 100
```

```
                                              Available systems
┌─────────────────────────┬──────────────┬────────────────┬──────────────────────────┬─────────────────────────────────┐
│ Customer                │ System       │ Mandant        │ Description              │ User                            │
╞═════════════════════════╪══════════════╪════════════════╪══════════════════════════╪═════════════════════════════════╡
│ BESTCUSTOMER            │ XXX          │ 100            │ Dev                      │ XXX                             │
└─────────────────────────┴──────────────┴────────────────┴──────────────────────────┴─────────────────────────────────┘
```

3. You can skip mandant and type 'sap list system'

```cmd
sap list xxx
```

```
                                              Available systems
┌─────────────────────────┬──────────────┬────────────────┬──────────────────────────┬─────────────────────────────────┐
│ Customer                │ System       │ Mandant        │ Description              │ User                            │
╞═════════════════════════╪══════════════╪════════════════╪══════════════════════════╪═════════════════════════════════╡
│ BESTCUSTOMER            │ XXX          │ 100            │ Dev                      │ XXX                             │
└─────────────────────────┴──────────────┴────────────────┴──────────────────────────┴─────────────────────────────────┘
```

4. Or you can skip system and leave mandant then type 'sap list % mandant'

```cmd
sap list % 200
```

```
                                              Available systems
┌─────────────────────────┬──────────────┬────────────────┬──────────────────────────┬─────────────────────────────────┐
│ Customer                │ System       │ Mandant        │ Description              │ User                            │
╞═════════════════════════╪══════════════╪════════════════╪══════════════════════════╪═════════════════════════════════╡
│ BESTCUSTOMER            │ YYY          │ 200            │ Test                     │ XXX                             │
└─────────────────────────┴──────────────┴────────────────┴──────────────────────────┴─────────────────────────────────┘
```

5. If you'd like to list information about system for a specific customer then type 'sap list -c customer_name'

```cmd
sap list -c bestcustomer
```

```
                                              Available systems
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Dev                         │ XXX         │
│ BESTCUSTOMER                   │ YYY               │ 200                 │ Test                        │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

6. To list systems with a specific user - use the following command

```cmd
sap list -u username 
```

7. To list systems with a specific description - use the following command

```cmd
sap list -d system_description 
```

8. To list systems with an url and autotype sequence - just add '-url' option to any command above

```cmd
sap list yyy -url
```

```
                                              Available systems
┌────────────────────┬───────────┬─────────────┬───────────────┬─────────┬─────────────┬────────────────────────────┐
│ Customer           │ System    │ Mandant     │ Description   │ User    │ URL         │ Autotype sequence          │
╞════════════════════╪═══════════╪═════════════╪═══════════════╪═════════╪═════════════╪════════════════════════════╡
│ BESTCUSTOMER       │ YYY       │ 200         │ Dev           │ XXX     │ www.sap.com │ {USER}{TAB}{PASS}{ENTER}   │
└────────────────────┴───────────┴─────────────┴───────────────┴─────────┴─────────────┴────────────────────────────┘
```

9. To list systems with password - just add '-v' option to any command above

```cmd
sap list xxx -v
```

```
                                              Available systems
┌───────────────────────────┬───────────────┬─────────────────┬─────────────────────────┬───────────┬──────────────────┐
│ Customer                  │ System        │ Mandant         │ Description             │ User      │ Password         │
╞═══════════════════════════╪═══════════════╪═════════════════╪═════════════════════════╪═══════════╪══════════════════╡
│ BESTCUSTOMER              │ XXX           │ 100             │ Dev                     │ XXX       │ 12345678         │
└───────────────────────────┴───────────────┴─────────────────┴─────────────────────────┴───────────┴──────────────────┘
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Information about passwords will be deleted from screen in 10                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

10. You can request information with incomplete values

For example, you remember part of customer's name - 'cust'

```cmd
sap list -c cust
```

A list of systems will be displayed with the customer's name that contains a "cust"

```
                                              Available systems
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Dev                         │ XXX         │
│ BESTCUSTOMER                   │ YYY               │ 200                 │ Test                        │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

The same works for any command's arguments and options.

If you remember first values and last values, but don't remember values in between - use '%' as delimiter
For example: option '-c be%er' will find all customer which have 'be' at the beginning and 'er' at the end.

## sap run

To launch sap system, 'sap run' command is used.

1. If you run 'sap run' without any options

```cmd
sap run 
```

then the list of all possible sap systems will be printed. And you have to choose which system you want to launch.

```
                                              Available systems
┌───────┬───────────────────────┬─────────────┬───────────────┬────────────────────────┬───────────────────────────────┐
│ Id    │ Customer              │ System      │ Mandant       │ Description            │ User                          │
╞═══════╪═══════════════════════╪═════════════╪═══════════════╪════════════════════════╪═══════════════════════════════╡
│ 1     │ BESTCUSTOMER          │ XXX         │ 100           │ Dev                    │ XXX                           │
│ 2     │ BESTCUSTOMER          │ YYY         │ 200           │ Test                   │ XXX                           │
└───────┴───────────────────────┴─────────────┴───────────────┴────────────────────────┴───────────────────────────────┘


Choose a system you want to login. Available values from 1 to 2:
>>>: 2

                                   Trying to LAUNCH the following system
┌──────────────────────┬──────────────────┬────────────────────┬───────────────────────────┬─────────────────────────┐
│ Customer             │ System           │ Mandant            │ Description               │ User                    │
╞══════════════════════╪══════════════════╪════════════════════╪═══════════════════════════╪═════════════════════════╡
│ BESTCUSTOMER         │ YYY              │ 200                │ Test                      │ XXX                     │
└──────────────────────┴──────────────────┴────────────────────┴───────────────────────────┴─────────────────────────┘
```

2. You can specify system and mandant, or specify only one of the parameters - either system or mandant (use '% mandant'
   options)

```cmd
sap run xxx 
```

As soon as only one record is found then this system is launched. If we have several records then you have to choose
a system to launch the way we did it with 'sap run' command without any options.

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘


                                   Trying to LAUNCH the following system
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Dev                         │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

3. sap run with additional options

You can try to launch sap system with additional options.

```
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --user -u TEXT Request a SAP system by user                                                                         │
│ --customer -c TEXT Request a SAP system by customer                                                                 │                                                                
│ --description -d TEXT Request a SAP system by description                                                           │
│ --language -l TEXT Logon language                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

For example, by user

```cmd
sap run -u xxx
```

Looking for a system in the database with a specific user and all results are printed. If results contain several
records then you need to choose a system you want to launch.

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
│ 2       │ BESTCUSTOMER                 │ YYY             │ 200               │ Test                     │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘

Choose a system you want to login. Available values from 1 to 2:
>>>: 1

                                   Trying to LAUNCH the following system
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Dev                         │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

4. launching specific sap command

You can launch specific command at sap system login: transaction (with parameters), report or system command.

```
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --transaction     -t      TEXT  Run transaction                                                                     │
│ --system_command  -s      TEXT  Run system_command: /n, /o, /i, /nend, /nex, /*<transaction_code>,                  │
│                                 /n<transaction_code>, /o<transaction_code>, /h                                      │
│ --report          -r      TEXT  Run report (report name for SE38 transaction)                                       │
│ --parameter       -p      TEXT  Transaction's parameters                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Trying to launch XXX system with transaction, for example, tr. SE11

```cmd
sap run xxx -t se11
```

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘


              Trying to LAUNCH the following system with transaction SE11
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Dev                         │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

also you can specify additional parameters - parameter's value for transaction. For example, for tr. SE11 - table name

```cmd
sap run xxx -t se11 -p t001
```

Trying to launch XXX system with system command

```cmd
sap run xxx -s /nex
```

This will force all opened XXX sap systems to close.

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘


            Trying to LAUNCH the following system with system command /NEX
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Dev                         │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

Trying to launch XXX system with report RFITEMAP

```cmd
sap run xxx -r RFITEMAP
```

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘


              Trying to LAUNCH the following system with report RFITEMAP
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Dev                         │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

5. launching web version of sap system or other site:

If you've specified an url for sap system then it is possible to run it in a web browser.

Let's take a look at system with url.

```cmd
sap list yyy -url
```

```
                                              Available systems
┌──────────────────┬───────────┬────────────┬────────────────┬────────┬────────────────┬───────────────────────────────┐
│ Customer         │ System    │ Mandant    │ Description    │ User   │ URL            │ Autotype sequence             │
╞══════════════════╪═══════════╪════════════╪════════════════╪════════╪════════════════╪═══════════════════════════════╡
│ BESTCUSTOMER     │ YYY       │ 200        │ Test           │ XXX    │ www.sap.com    │ {USER}{TAB}{PASS}{ENTER}      │
└──────────────────┴───────────┴────────────┴────────────────┴────────┴────────────────┴───────────────────────────────┘
```

URL - www.sap.com will be launched.
YYY system have autotype sequence by default: {USER}{TAB}{PASS}{ENTER}. It means that USER id will be pasted into Login
field (if login field have focus), then TAB will be pressed to get to PASSWORD field, and PASSWORD will be pasted, then
ENTER will be pressed. Voila!

```cmd
sap run yyy -w
```

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Launching web site: Launching web site: www.sap.com (Test of BESTCUSTOMER)                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Waiting web site to load: 4 seconds                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

6. launching new connection to the same system.

If you need to open new connection (let's say, you have 6 windows of XXX system opened, and you need more!!!) then you
can use '-n' option

```cmd
sap run xxx -n
```

7. launching existing sap system in your database with user/password not in your database. So-called external user.

```cmd
sap run yyy 200 -eu
```

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘

Enter external user id: external_user_id
Enter password for external user: 12345678

                          Trying to LAUNCH the following system with EXTERNAL USER
┌────────────────────┬────────────────┬──────────────────┬──────────────────────────┬──────────────────────────────────┐
│ Customer           │ System         │ Mandant          │ Description              │ User                             │
╞════════════════════╪════════════════╪══════════════════╪══════════════════════════╪══════════════════════════════════╡
│ BESTCUSTOMER       │ YYY            │ 200              │ Dev                      │ EXTERNAL_USER_ID                 │
└────────────────────┴────────────────┴──────────────────┴──────────────────────────┴──────────────────────────────────┘
```

## sap update

If you need to update any parameter of sap system in the database then you can use command 'sap update'

```cmd
sap update xxx
```

List of available systems will be printed. Then you'll be prompted to enter parameters. In [] brackets values from
database will be printed. If you don't need to change this parameter just press Enter. If you need to change parameters
then type new value.

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Dev                      │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘

Enter new password [12345678]: 87654321
Enter Customer [BESTCUSTOMER]:
Enter system description [Dev]: Development
Enter URL []:
Enter Autotype sequence [{USER}{TAB}{PASS}{ENTER}]:


                                       The following system is UPDATED
┌───────────────────────────┬───────────────┬─────────────────┬─────────────────────────┬───────────┬──────────────────┐
│ Customer                  │ System        │ Mandant         │ Description             │ User      │ Password         │
╞═══════════════════════════╪═══════════════╪═════════════════╪═════════════════════════╪═══════════╪══════════════════╡
│ BESTCUSTOMER              │ XXX           │ 100             │ Development             │ XXX       │ 87654321         │
└───────────────────────────┴───────────────┴─────────────────┴─────────────────────────┴───────────┴──────────────────┘
Information about passwords will be deleted from screen in 10:
```

## sap delete

To delete record from database use command 'sap delete'. Type command and follow the instructions.

```cmd
sap delete xxx
```

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ XXX             │ 100               │ Development              │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘

                                   Trying to DELETE the following systtem
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Development                 │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
Do you really want to delete the system? [y/n]: y


                                The following system is DELETED from database
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Development                 │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

## sap debug

You have two possibilities:

1. Start debugging already opened system.

If you have already opened system which you need to debug then use command 'sap debug'. Debug is always launched for the
latest opened sap system's window.
So **Open the window you need to debug** and run command.

```cmd
sap debug yyy
```

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ YYY             │ 200               │ Test                     │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘


                                    Trying to DEBUG the following system
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ YYY               │ 200                 │ Test                        │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

2. Create debug file

```cmd
sap debug -f
```

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│     # DEBUG                                                                                                          │
│                                                                                                                      │
│     C:\Users\gababitskii\AppData\Local\sap\DEBUG.TXT file will be created.                                           │
│     After creation, a folder with DEBUG.TXT file will be opened                                                      │
│     Drag the file to the SAP system to start debug mode                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## sap backup

You can create backup with 'sap backup' command. Backup file is a password-protected archive.

It will contain the following files inside:

1. SAPUILandscape.xml - saplogon configuration file with all system from saplogon
2. public_key.txt - public encryption file
3. private_key.txt - private encryption file
4. sap_config.ini - configuration file
5. sap_cmd.db - database

```cmd
sap backup
```

```
Password: 12345678
Repeat for confirmation: 12345678
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Backup succesfully created: C:\Users\<USERNAME>\AppData\Local\sap\backup_2022.07.06-02.22.09.zip                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## sap pw

If you need only a password for specific sap system then you can use 'sap pw' command
This can be useful when you are already logged in one system and password is requested for the other system.
For example tr. STMS when you transport request into another system.

```cmd
sap pw yyy
```

```
                                              Available systems
┌─────────┬──────────────────────────────┬─────────────────┬───────────────────┬──────────────────────────┬────────────┐
│ Id      │ Customer                     │ System          │ Mandant           │ Description              │ User       │
╞═════════╪══════════════════════════════╪═════════════════╪═══════════════════╪══════════════════════════╪════════════╡
│ 1       │ BESTCUSTOMER                 │ YYY             │ 200               │ Test                     │ XXX        │
└─────────┴──────────────────────────────┴─────────────────┴───────────────────┴──────────────────────────┴────────────┘
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Password is copied into clipboard.                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Sensitive ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ If you use Clipboard managers, you should add PY.EXE, CMD.EXE applications to the exclusion list,                    │
│ in order to keep sensitive information safe from copying to clipboard manager.                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Clipboard will be cleared in 10 seconds.                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
0
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Clipboard is cleared.                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## sap paradd

Let's say you want to open tr. SE11 with the value of the table name already entered.
You can use command 'sap run system mandant -t se11'. All you need right now is to add option '-p tablename'
In order to you this possibility you need to add parameter for transaction.

0. Open tr. SE11
1. Give focus on 'Database table' field and press F1 key on keyboard.
2. Press 'Technical information' button.
3. Copy value from 'Screen Field' field.
4. run 'sap paradd' command in terminal and follow the instruction. Transaction - SE11, Parameter - RSRD1-TBMA_VAL

[![](resources\images\screen_field.png)]

```cmd
sap paradd
```

```
Transaction: se11
Parameter: RSRD1-TBMA_VAL

                                    Available transactions and parameters
┌─────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────┐
│ Transaction                                         │ Parameters                                                     │
╞═════════════════════════════════════════════════════╪════════════════════════════════════════════════════════════════╡
│ SE11                                                │ RSRD1-TBMA_VAL                                                 │
└─────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────┘
```

Now you can open sap system with tr. SE11 and table id T001:

```cmd
sap run xxx -t se11 -p t001
```

If you have several fields then you can enter them with ',' delimiter.
For example, tr. FB03 "Display Fi document" have 3 fields: Document (Screen Field - RF05L-BELNR), Company code (Screen
Field - RF05L-BUKRS) and Year (Screen Field - RF05L-GJAHR)

```cmd
sap paradd
```

```
Transaction: fb03
Parameter: RF05L-BELNR,RF05L-BUKRS,RF05L-GJAHR

                                    Available transactions and parameters
┌───────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────┐
│ Transaction                   │ Parameters                                                                           │
╞═══════════════════════════════╪══════════════════════════════════════════════════════════════════════════════════════╡
│ FB03                          │ RF05L-BELNR,RF05L-BUKRS,RF05L-GJAHR                                                  │
└───────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘
```

Now you can launch sap system with tr. FB03 and give all parameters delimited by ',' exactly as they were added into
database earlier - document number, company code, year.

```cmd
sap run dhv 100 -tfb03 -p100000023,01,2019
```

```
                                              Available systems
┌────────┬─────────────────────────┬───────────────┬─────────────────┬────────────────────────┬────────────────────────┐
│ Id     │ Customer                │ System        │ Mandant         │ Description            │ User                   │
╞════════╪═════════════════════════╪═══════════════╪═════════════════╪════════════════════════╪════════════════════════╡
│ 1      │ BESTCUSTOMER            │ XXX           │ 200             │ Dev                    │ XXX                    │
└────────┴─────────────────────────┴───────────────┴─────────────────┴────────────────────────┴────────────────────────┘


   Trying to LAUNCH the following system with transaction FB03 -> 100000023,01,2019
┌────────────────────────────────┬───────────────────┬─────────────────────┬─────────────────────────────┬─────────────┐
│ Customer                       │ System            │ Mandant             │ Description                 │ User        │
╞════════════════════════════════╪═══════════════════╪═════════════════════╪═════════════════════════════╪═════════════╡
│ BESTCUSTOMER                   │ XXX               │ 100                 │ Development                 │ XXX         │
└────────────────────────────────┴───────────────────┴─────────────────────┴─────────────────────────────┴─────────────┘
```

## sap parlist

To display all transactions and their parameters (Screen fields) run the following command

```cmd
sap parlist
```

```
                                   Available transactions and parameters
┌───────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────┐
│ Transaction                   │ Parameters                                                                           │
╞═══════════════════════════════╪══════════════════════════════════════════════════════════════════════════════════════╡
│ SE11                          │ RSRD1-TBMA_VAL                                                                       │
│ FB03                          │ RF05L-BELNR,RF05L-BUKRS,RF05L-GJAHR                                                  │
└───────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘
```

Or you can display parameters of specific transaction - then run command 'sap parlist' with '-t transaction' option

```cmd
sap parlist -t fb03
```

```
                                    Available transactions and parameters
┌──────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ Transaction                      │ Parameters                                                                        │
╞══════════════════════════════════╪═══════════════════════════════════════════════════════════════════════════════════╡
│ FB03                             │ RF05L-BELNR,RF05L-BUKRS,RF05L-GJAHR                                               │
└──────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```

## sap parupdate

If you need to update parameters for specific transaction run

```cmd
sap parupdate
```

```
  Available transactions and parameters
┌─────────┬────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┐
│ Id      │ Transaction                │ Parameters                                                                    │
╞═════════╪════════════════════════════╪═══════════════════════════════════════════════════════════════════════════════╡
│ 1       │ SE11                       │ RSRD1-TBMA_VAL                                                                │
│ 2       │ FB03                       │ RF05L-BELNR,RF05L-BUKRS,RF05L-GJAHR                                           │
└─────────┴────────────────────────────┴───────────────────────────────────────────────────────────────────────────────┘

Choose a transaction with parameter. Available values from 1 to 18:
>>>: 1
```

Enter new value (for example RSRD1-VIMA_VAL - screen field for View) or press Enter to leave the old value

```
Enter new parameters for transaction SE11 [RSRD1-TBMA_VAL]: RSRD1-VIMA_VAL

                                          The following system is UPDATED
┌─────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Transaction                                                 │ Parameters                                             │
╞═════════════════════════════════════════════════════════════╪════════════════════════════════════════════════════════╡
│ SE11                                                        │ RSRD1-VIMA_VAL                                         │
└─────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

## sap pardel

To delete transaction and its parametes run

```cmd
sap pardel
```

```
                                    Available transactions and parameters
┌──────────┬───────────────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Id       │ Transaction                   │ Parameters                                                                │
╞══════════╪═══════════════════════════════╪═══════════════════════════════════════════════════════════════════════════╡
│ 1.       │ SE11                          │ RSRD1-TBMA_VAL                                                            │
│ 2.       │ FB03                          │ RF05L-BELNR,RF05L-BUKRS,RF05L-GJAHR                                       │
└──────────┴───────────────────────────────┴───────────────────────────────────────────────────────────────────────────┘


Choose a transaction with parameter. Available values from 1 to 2:
>>>: 2

Do you really want to delete the system? [y/n]: y


                                    The following parameter is DELETED from database
┌─────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────┐
│ Transaction                                         │ Parameters                                                     │
╞═════════════════════════════════════════════════════╪════════════════════════════════════════════════════════════════╡
│ FB03                                                │ RF05L-BELNR,RF05L-BUKRS,RF05L-GJAHR                            │
└─────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────┘
```

## sap config

You can use the following commands for working with config

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Enter one of subcommands:                                                                                            │
│                                                                                                                      │
│      -create       Create config file. For techincal purpuse. Use "sap start" to create config                       │
│      -open         Open config file                                                                                  │
│      -folder       Open config folder                                                                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. In order to edit config file run the following command

```cmd
sap config -open 
```

```
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Opening file: C:\Users\USERNAME\AppData\Local\sap\sap_config.ini                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

2. Open folder with config file. There you can also find newly created backup files

```cmd
sap config -folder 
```

```
╭─ Message ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Opening folder: C:\Users\gababitskii\AppData\Local\sap                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## sap logon

If you need to open saplogon application only then use 'sap logon' command

## sap --version

In order to check version of sap command line tool run this command

```cmd
sap --version 
```

```
sap, version 3.0
```

## sap about

If you need to take a look at information about SAPLogon then use this command:

```cmd
sap about 
```

[![sap_about](resources\images\sap_about.png)]

## sap shortcut

To display information about shortcut.exe file use this command:

```cmd
sap shortcut 
```

[![sap_shortcut](resources\images\sap_shortcut.png)]

## other command

in progress

# Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# License

[MIT](https://choosealicense.com/licenses/mit/)

# Alternatives:

1. [KeePass](https://blogs.sap.com/2012/01/29/using-keepass-instead-of-sap-logon/)
2. [KeePass Plugin](https://edp.bg/kpsapbutton-project/)