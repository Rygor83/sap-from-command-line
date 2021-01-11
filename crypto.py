#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

from config import *


class Crypto(object):
    public_file = 'public_key.txt'
    private_file = 'private_key.txt'

    @staticmethod
    def generate_keys():
        """
        Создание ключей шифрования: публичный ключ и приватный ключа
        """

        conf = Config()
        conf.get_config()
        path_public_key = conf.config['KEYS'][Crypto.public_file]
        path_private_key = conf.config['KEYS'][Crypto.private_file]

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
            print(colored(f"Ключи шифрования созданы: {Crypto.public_file} и {Crypto.private_file}", 'green'))
            print('Необходимо указать их расположение в файле *.ini')
            print(colored(f"Файл {Crypto.private_file} должен находиться в зашифрованном хранилище", 'white', 'on_red'))
            input('Нажмите для продолжения')
        else:
            print(colored("Ключи шифрования уже созданы", 'yellow'))
            input('Нажмите для продолжения')
            sys.exit()

    @staticmethod
    def save_key(pem, file_name):
        with open(file_name, "w") as file:
            for item in pem.splitlines():
                # print(item)
                file.write(item.decode() + '\n')

    @staticmethod
    def encrypto(password):
        public_key_file = Crypto.get_key(Crypto.public_file)

        try:
            with open(public_key_file, "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())
        except FileNotFoundError:
            print(colored('Публичный ключ шифрования не доступен. Проверьте доступ', 'yellow'))
            input('Нажмите для продолжения')
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
        private_key_file = Crypto.get_key(Crypto.private_file)

        try:
            with open(private_key_file, "rb") as key_file:
                private_key = serialization.load_pem_private_key(key_file.read(), password=None,
                                                                 backend=default_backend())
        except FileNotFoundError:
            print(colored('Приватный ключ шифрования не доступен. Проверьте доступ', 'yellow'))
            input('Нажмите для продолжения')
            sys.exit()

        decrypted_data = private_key.decrypt(encrypted_password,
                                             padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None)).decode()
        return decrypted_data

    @staticmethod
    def get_key(key_name):
        conf = Config()
        conf.get_config()
        key_file = conf.config['KEYS'][key_name]
        if not key_file.endswith('.txt'):
            print(colored(f"в ini файле не найден путь к {key_name} ключу шифрования", 'yellow'))
            input('Нажмите для продолжения')
            sys.exit()
        return key_file
