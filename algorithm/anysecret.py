#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile, os
from Crypto.Cipher import AES
from Crypto.Util import Padding

MAGIC_NUMBER = "PASSCARE"
CHECK_WORDS = "LEGAL INSTITUTION IS THE ONLY WAY LEADS TO A MORDEN SOCIETY."

def _unarchive(zip_path: str):
    """
    Unarchive the zip file.
    - zip_path: the zip file path on the disk.
    """
    zipFile = zipfile.ZipFile(zip_path)
    zipFile.extract(".info", '.')
    zipFile.close()

def _check_info_file(bytes: bytearray, secret: str) -> bool:
    """
    Check .info file format.
    """
    # Check magic number of .info file.
    magic_number_bytes = MAGIC_NUMBER.encode('utf-8')
    magic_number_bytes_length = len(magic_number_bytes)
    magic_number_pass = magic_number_bytes == bytes[0:magic_number_bytes_length]
    if not magic_number_pass:
        return False
    # Check secret.
    iv = secret[0:16]
    key = secret[16:48]
    check_words_bytes = _aes_encrypt(iv, key, CHECK_WORDS)
    check_words_bytes_length = len(check_words_bytes)
    check_words_pass = check_words_bytes == bytes[magic_number_bytes_length : magic_number_bytes_length+check_words_bytes_length]
    if not check_words_pass:
        return False
    # .info file check passed.
    return True

def _aes_encrypt(iv: str, key: str, text: str) -> str:
    """
    Use AES algorithm to encrypt text.
    - iv: the iv of AES
    - key: the key of AES
    - text: the text to encrypt
    """
    iv = iv.encode('utf-8')
    key = key.encode('utf-8')
    text = text.encode('utf-8')
    padded_plaintext = Padding.pad(text, AES.block_size)
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.encrypt(padded_plaintext) 

def _aes_decrypt(iv: str, key: str, bytes) -> str:
    """
    Use AES algorithm to decrypt bytes.
    - iv: the iv of AES
    - key: the key of AES
    - bytes: bytes to decrypt
    """
    iv = iv.encode('utf-8')
    key = key.encode('utf-8')
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.decrypt(bytes).decode('utf-8')

def _is_file_exists(path: str) -> bool:
    """
    Check if file of given path exists.
    - path: the path of file to check
    """
    return path is not None and len(path) > 0 and os.path.exists(path)

def _read_bytes(file_path: str) -> bytearray:
    """
    Read file into byte array.
    - file_path: the path of file to read.
    """
    with open(file_path, 'rb') as f:
        bytes = f.read()
    f.close()
    return bytes

def _decrypt_data(bytes: bytearray, secret: str):
    """
    Decrypt data.
    """
    magic_number_bytes = MAGIC_NUMBER.encode('utf-8')
    magic_number_bytes_length = len(magic_number_bytes)
    iv = secret[0:16]
    key = secret[16:48]
    check_words_bytes = _aes_encrypt(iv, key, CHECK_WORDS)
    check_words_bytes_length = len(check_words_bytes)
    # Decrypt data.
    data_start = magic_number_bytes_length + check_words_bytes_length
    data_bytes = bytes[data_start:]
    data_decrypted = _aes_decrypt(iv, key, data_bytes)
    print(data_decrypted)

def _decrypt(data_path: str, secret: str) -> bool:
    """
    Decrypt the data zip file.
    - data_path: the path of data zip file.
    """
    if not _is_file_exists(data_path):
        print('Failed to decrypt the data file: the file not found on disk.')
        return False
    _unarchive(data_path)
    bytes = _read_bytes('.info')
    if not _check_info_file(bytes, secret):
        print("Failed to decrypt the data file: file format error.")
        return False
    _decrypt_data(bytes, secret)
    
if __name__ == "__main__":
    """
    Entrance.
    """
    zip_file_path = "" # Input your zip file path here.
    secret = "" # Input your app secret here.
    _decrypt(zip_file_path, secret)
