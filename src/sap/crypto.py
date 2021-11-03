#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

import sap.config

import click
import sys
import os

import sap.utilities as utilities

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


class Crypto(object):
    public = 'public_key.txt'
    private = 'private_key.txt'

    public_file = os.path.join(utilities.path(), public)
    private_file = os.path.join(utilities.path(), private)

    @staticmethod
    def generate_keys():
        """
        Создание ключей шифрования: публичный ключ и приватный ключа
        """

        cfg = sap.config.Config()
        _config = cfg.read()
        path_public_key = _config.public_key_path
        path_private_key = _config.private_key_path

        if not os.path.isfile(path_public_key) and not os.path.isfile(path_private_key):
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            Crypto.save_key(private_pem, Crypto.private_file)

            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
            Crypto.save_key(public_pem, Crypto.public_file)
            click.echo(click.style(f"Ключи шифрования созданы: {Crypto.public_file} и {Crypto.private_file}",
                                   **utilities.color_success))
            click.echo(click.style(f"Ключи шифрования созданы: {Crypto.public_file} и {Crypto.private_file}",
                                   **utilities.color_success))
            click.echo('Необходимо указать их расположение в файле *.ini')
            click.echo(click.style(f"Файл {Crypto.private_file} должен находиться в зашифрованном хранилище",
                                   **utilities.color_sensitive))
            click.pause('Нажмите для продолжения ...')
        else:
            click.echo(click.style("Ключи шифрования уже созданы", **utilities.color_warning))
            sys.exit()

    @staticmethod
    def save_key(pem, file_name):
        with open(file_name, "w") as file:
            for item in pem.splitlines():
                # click.echo(item)
                file.write(item.decode() + '\n')

    @staticmethod
    def encrypto(password):
        public_key_file = Crypto.get_key(Crypto.public)

        try:
            with open(public_key_file, "rb") as key_file:
                message = key_file.read()
                public_key = serialization.load_pem_public_key(message, backend=default_backend())
        except FileNotFoundError:
            click.echo(
                click.style('Публичный ключ шифрования не доступен. Проверьте доступ', **utilities.color_warning))
            sys.exit()

        encrypted_data = public_key.encrypt(
            password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data

    @staticmethod
    def decrypto(encrypted_password):
        private_key_file = Crypto.get_key(Crypto.private)

        try:
            with open(private_key_file, "rb") as key_file:
                message = key_file.read()
                private_key = serialization.load_pem_private_key(message, password=None,
                                                                 backend=default_backend())
        except FileNotFoundError:
            click.echo(
                click.style('Приватный ключ шифрования не доступен. Проверьте доступ', **utilities.color_warning))
            sys.exit()

        decrypted_data = private_key.decrypt(encrypted_password,
                                             padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None)).decode()

        return decrypted_data

    @staticmethod
    def get_key(key_type):
        cfg = sap.config.Config()
        _config = cfg.read()

        if key_type == Crypto.private:
            return _config.private_key_path
        elif key_type == Crypto.public:
            return _config.public_key_path
