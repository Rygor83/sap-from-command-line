#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------
import pytest
from sap.crypto import Crypto
import os


@pytest.fixture
def temp_crypto(tmpdir):
    public = os.path.join(tmpdir, 'public_key.txt')
    private = os.path.join(tmpdir, 'private_key.txt')
    cr = Crypto(public, private)
    yield cr
    cr.remove_keys()


def test_create_crypto_files(temp_crypto):
    temp_crypto.generate_keys()
    assert os.path.isfile(temp_crypto.public_key_path) is True and os.path.isfile(temp_crypto.private_key_path) is True


def test_encrypt(temp_crypto):
    temp_crypto.generate_keys()
    password = '12345'
    encrypted_password = temp_crypto.encrypto(str.encode(password))
    decrypted_password = temp_crypto.decrypto(encrypted_password)
    assert decrypted_password == password
