#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Passwords encryption with RSA for sap systems """

import os
import click
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from sap import utilities
from sap.api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME
from sap.exceptions import EncryptionKeysAlreadyExist


class Crypto:
    """ Encryption RSA class """

    def __init__(self, public_key_path: str = '', private_key_path: str = ''):
        self.public_key_file_name = PUBLIC_KEY_NAME
        self.private_key_file_name = PRIVATE_KEY_NAME
        self.public_key_path = public_key_path if public_key_path else os.path.join(
            utilities.path(), self.public_key_file_name)
        self.private_key_path = private_key_path if private_key_path else os.path.join(
            utilities.path(), self.private_key_file_name)

    def generate_keys(self):
        """ Generate RSA encryption keys: public, private """

        if not os.path.isfile(self.public_key_path) and not os.path.isfile(self.private_key_path):
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            self.save_key(private_pem, self.private_key_path)

            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
            self.save_key(public_pem, self.public_key_path)
        else:
            raise EncryptionKeysAlreadyExist(public_path=self.public_key_path, private_path=self.private_key_path)

    def save_key(self, pem, file_name):
        """ Save RSA keys """
        with open(file_name, "w", encoding='utf-8') as file:
            for item in pem.splitlines():
                # click.echo(item)
                file.write(item.decode() + '\n')

    def encrypto(self, password):
        """ Encrypt sensitive info """
        try:
            with open(self.public_key_path, "rb") as key_file:
                message = key_file.read()
                public_key = serialization.load_pem_public_key(message, backend=default_backend())
        except FileNotFoundError as err:
            click.echo(
                click.style(f"\nPublic key does not exist. \nPath: {self.public_key_path}", **utilities.color_warning))
            raise click.Abort from err

        encrypted_data = public_key.encrypt(
            password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data

    def decrypto(self, encrypted_password):
        """ Decrypt sensitive info """
        try:
            with open(self.private_key_path, "rb") as key_file:
                message = key_file.read()
                private_key = serialization.load_pem_private_key(message, password=None,
                                                                 backend=default_backend())
        except FileNotFoundError as err:
            click.echo(
                click.style(f"\nPrivate key does not exist. \nPath: {self.private_key_path}",
                            **utilities.color_warning))
            raise click.Abort from err

        decrypted_data = private_key.decrypt(encrypted_password,
                                             padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None)).decode()

        return decrypted_data

    def remove_keys(self):
        """ Remove encryption keys """
        os.remove(self.private_key_path)
        os.remove(self.public_key_path)

