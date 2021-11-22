#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
""" Custom Exceptions """


# TODO: оформить правильно все exceptions

class ConfigExists(Exception):
    """Base class for other exceptions"""

    def __init__(self, config_path, message="sap_config.ini already exists"):
        self.message = f"{message}. Path: {config_path}"
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
