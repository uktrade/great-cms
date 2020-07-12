from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken


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
        message_b = message.encode('utf-8')
        ciphertext_b = Fernet(self.key).encrypt(message_b)
        return ciphertext_b.decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        try:
            ciphertext_b = Fernet(self.key).decrypt(ciphertext.encode('utf-8'))
            return ciphertext_b.decode('utf-8')
        except InvalidToken:
            return ''
