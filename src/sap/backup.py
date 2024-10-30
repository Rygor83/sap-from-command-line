#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Backup api """

from pathlib import Path
from datetime import datetime
import pyzipper


class Backup:
    """
    Class for working with backup file
    """

    comment = r"""
                  1. Place 'SAPUILandscape.xml' to '%APPDATA%\SAP\Common' folder
                  2. Place 'sap_config.ini' to 'c:\Users\<USERNAME>\AppData\Local\SAP' folder
                  3. Other files - according to sap_config.ini paths
                  Or you can place whenever you want, just enter new paths to sap_config.ini
                  !!! And remember that files 'database.db' and 'private_key.txt' must be stored in secure place"""

    def __init__(self, password, backup_path, files):
        self.password = password
        self.backup_path = Path(backup_path)
        self.files = files
        self.backup_file_path = Path()

    def create(self):
        """
        Create backup file
        """
        pwd = str.encode(self.password)

        back_file_name = f'backup_{datetime.now().strftime("%Y.%m.%d-%I.%M.%S")}.zip'
        self.backup_file_path = Path(self.backup_path / back_file_name)
        with pyzipper.AESZipFile(self.backup_file_path, 'w', compression=pyzipper.ZIP_LZMA,
                                 encryption=pyzipper.WZ_AES) as zip_file:
            zip_file.setpassword(pwd)

            # Adding files into backup archive:
            #TODO: Проверять, что путь сущетсвует иначе будет дамп
            #  FileNotFoundError: [WinError 3] The system cannot find the path
            #  specified: 'z:\\db\\sap_cmd.db'
            for file in self.files:
                zip_file.write(file, Path(file).name)

            zip_file.comment = self.comment.encode()

        return self.backup_file_path

    def delete(self):
        """
        Delete backup file
        """
        self.backup_file_path.unlink()
