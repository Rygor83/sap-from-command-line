#  ------------------------------------------
#   Copyright (c) Rygor. 2021.
#  ------------------------------------------

""" Encryption system Tests """

import pytest
from sap.crypto import Crypto
import os

from api import PUBLIC_KEY_NAME, PRIVATE_KEY_NAME


@pytest.fixture
def temp_crypto(tmpdir):
    """
    Create public and private encryption keys
    """
    public = os.path.join(tmpdir, PUBLIC_KEY_NAME)
    private = os.path.join(tmpdir, PRIVATE_KEY_NAME)
    cr = Crypto(public, private)
    yield cr
    cr.remove_keys()


def test_create_crypto_files(temp_crypto):
    """ Test if encryption keys are created"""
    temp_crypto.generate_keys()
    assert os.path.isfile(temp_crypto.public_key_path) is True and os.path.isfile(temp_crypto.private_key_path) is True


def test_encrypt(temp_crypto):
    """ Encode and decode string """
    temp_crypto.generate_keys()
    password = '12345'
    encrypted_password = temp_crypto.encrypto(str.encode(password))
    decrypted_password = temp_crypto.decrypto(encrypted_password)
    assert decrypted_password == password
