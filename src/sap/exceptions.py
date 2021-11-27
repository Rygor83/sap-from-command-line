#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
""" Custom Exceptions """


# TODO: оформить правильно все exceptions

class ConfigExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, config_path, message="sap_config.ini already exists"):
        self.message = f"{message}. \nPath: {config_path}"
        super().__init__(self.message)


class ConfigDoesNotExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, path, message="sap_config.ini does not exist"):
        self.message = f"{message}. \nCheck path: {path}"
        super().__init__(self.message)


class FileDoesNotExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, path, file_name):
        self.message = f"Parameters {file_name}. Path does not exist: {path}"
        super().__init__(self.message)


class WrongPath(Exception):
    """Base class for other exceptions"""

    def __init__(self, file, path, message="Wrong path to"):
        self.message = f'{message} {file} file: {path}'
        super().__init__(self.message)


class DatabaseExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, db_path, message="Database already exists"):
        self.message = f"{message}. Path: {db_path}"
        super().__init__(self.message)


class DatabaseDoesNotExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, path, message="Database does not exist or there is no possibility for connection."):
        self.message = f"\n{message}. \nCheck the following path: {path}"
        super().__init__(self.message)


class WrongPath(Exception):
    """Base class for other exceptions"""

    def __init__(self, file, path, message="Wrong path to"):
        self.message = f'{message} {file} file: {path}'
        super().__init__(self.message)
