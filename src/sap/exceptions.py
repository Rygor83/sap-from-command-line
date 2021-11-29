#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
""" Custom Exceptions """


# ========================== CONFIG ==========================

class ConfigExists(Exception):
    """ Exception. Config file already exists """

    def __init__(self, config_path, message="SAP_CONFIG.INI already exists"):
        self.message = f"\n{message}. \nPath: {config_path}"
        super().__init__(self.message)


class ConfigDoesNotExists(Exception):
    """ Exception. Config file does not exist """

    def __init__(self, path, message="SAP_CONFIG.INI does not exist."):
        self.message = f"\n{message}. \nCheck path: {path} \nEither run 'sap start' or 'sap config -create' to create and edit config"
        super().__init__(self.message)


class WrongPath(Exception):
    """ Exception. SAP executables do not exist """

    def __init__(self, file, path, message="SAP executable does not exist:"):
        self.message = f'\n{message} {file} \nCheck the following path: {path}'
        super().__init__(self.message)


# ========================== DATABASE ==========================

class DatabaseExists(Exception):
    """ Exception. Database already exists """

    def __init__(self, db_path, message="Database already exists"):
        self.message = f"\n{message}. Path: {db_path}"
        super().__init__(self.message)


class DatabaseDoesNotExists(Exception):
    """Exception. Database does not exist"""

    def __init__(self, path, message="Database does not exist or there is no possibility for connection."):
        self.message = f"\n{message}. \nCheck the following path: {path}"
        super().__init__(self.message)


# ========================== CRYPTO ==========================

class PublicKeyAlreadyExists(Exception):
    """ Exception. Public key already exists """

    def __init__(self, file, path, message="Public key already exists"):
        self.message = f'\n{message} {file} file: {path}'
        super().__init__(self.message)


class PublicKeyDoesNotExist(Exception):
    """ Exception. Public key does not exist """

    def __init__(self, file, path, message="Public key does not exist"):
        self.message = f'\n{message} {file} file: {path}'
        super().__init__(self.message)


class PrivateKeyAlreadyExists(Exception):
    """ Exception. Public key already exists """

    def __init__(self, file, path, message="Private key already exists"):
        self.message = f'\n{message} {file} file: {path}'
        super().__init__(self.message)


class PrivateKeyDoesNotExist(Exception):
    """ Exception. Public key does not exist """

    def __init__(self, file, path, message="Private key does not exist"):
        self.message = f'\n{message} {file} file: {path}'
        super().__init__(self.message)


class EncryptionKeysAlreadyExist(Exception):
    """ Exception. Public key already exists """

    def __init__(self, public_path, private_path, message="Encryption keys already exist"):
        self.message = f'\n{message}: \nPrivate: {private_path} \nPublic: {public_path}'
        super().__init__(self.message)
