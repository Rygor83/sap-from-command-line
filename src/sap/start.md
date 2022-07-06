# Preparatory work
## Created files:

1. sap_config.ini - used to store information about all following files locations. Default location is "C:
   \Users\<USERNAME>\AppData\Local\sap" folder. Also contains some additional parameters. All parameters have description.
2. public_key.txt - used to encrypt passwords in database. Can be stored in any place. If you move it from default
   location then don't forget to put new place in sap_config.ini -> '[KEYS]' -> 'public_key_path'
3. private_key.txt - used to decrypt passwords. Must be stored in a secure place. For example,
   in [Bestcrypt](https://www.jetico.com/) container. Don't forget to put new place in sap_config.ini -> '[KEYS]' -> 'private_key_path'
4. database.db - used to store all information about SAP systems. Must be stored in secure place. For example, in
   [Bestcrypt](https://www.jetico.com/) container. Don't forget to put new place in sap_config.ini -> '[DATABASE]' -> '
   db_path'

## Extra work:

5. Find 'SAPSHCUT.EXE' file and put its location in sap_config.ini -> '[APPLICATION]' -> 'command_line_path'
5. Find 'SAPLOGON.EXE' file and put its location in sap_config.ini -> '[APPLICATION]' -> 'saplogon_path'

# Start working

To start work with SAP commands after preparatory work:
- type 'SAP ADD' to add sap system into database
- type 'SAP RUN <system id> <mandant num>' to launch sap system
- type 'SAP --HELP' to learn more about program
