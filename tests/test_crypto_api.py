#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

""" Encryption system Tests """


def test_create_crypto_files(temp_crypto):
    """ Test if encryption keys are created"""
    temp_crypto.generate_keys()
    assert temp_crypto.public_key_path.is_file() and temp_crypto.private_key_path.is_file()


def test_encrypt(temp_crypto):
    """ Encode and decode string """
    temp_crypto.generate_keys()
    password = '12345'
    encrypted_password = temp_crypto.encrypto(str.encode(password))
    decrypted_password = temp_crypto.decrypto(encrypted_password)
    assert decrypted_password == password
