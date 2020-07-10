import base64, re,os
import binascii
from Crypto.Cipher import AES
from Crypto import Random
from django.conf import settings
import base64
from Crypto.Cipher import AES
from base64 import b64encode,b64decode
from Crypto.Util import Counter
from cryptography.fernet import Fernet


class Fern:
    # """
    #   Usage:
    # encrypt('foo')
    # decrypt('CIPHERTEXT_ENCRYPTED_TEXT')
    # """
    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = settings.BETA_ENVIRONMENT

    def encrypt(self, message: str) -> str:
        # print(self.key)
        message_b = message.encode('utf-8')
        ciphertext_b = Fernet(self.key).encrypt(message_b)
        return ciphertext_b.decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        ciphertext_b = Fernet(self.key).decrypt(ciphertext.encode('utf-8'))
        return ciphertext_b.decode('utf-8')
