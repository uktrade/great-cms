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
    #   fernet = Fernet( settings.BETA_ENVIRONMENT[:16], 32)
    #   encryp_msg = fernet.encrypt( 'valid until XXX msec since epoch' )
    #   msg = fernet.decrypt( encryp_msg )
    #   print("'{}'".format(msg))
    # """
    #
    # def __init__(self, key):
    #     self.bs = AES.block_size
    #     self.key = key.encode()
    #
    # def encrypt(self, raw):
    #     raw = self._pad(raw)
    #     cipher = AES.new(self.key, AES.MODE_CTR)
    #     ct_bytes = cipher.encrypt(raw)
    #     # nonce = b64encode(cipher.nonce).decode('utf-8')
    #     return b64encode(ct_bytes).decode('utf-8')
    #     # return base64.b64encode(iv + cipher.encrypt(raw.encode()))
    #
    # def decrypt(self, enc):
    #     enc = base64.b64decode(enc)
    #     iv = enc[:AES.block_size]
    #     cipher = AES.new(self.key, AES.MODE_CTR, iv)
    #     return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
    #
    # def _pad(self, s):
    #     return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
    #
    # @staticmethod
    # def _unpad(s):
    #     return s[:-ord(s[len(s) - 1:])]
    def __init__(self, key):
        self.key = key

    def encrypt(self, message: bytes) -> bytes:
        print(self.key)
        return Fernet(self.key).encrypt(message.encode())

    def decrypt(self, token: bytes) -> bytes:
        return Fernet(self.key).decrypt(token.encode())
    # @staticmethod
    # def int_of_string(s):
    #     return int(s.hex(), 16)

    # def encrypt(self, message):
    #     encoded_message = message.encode()
    #     f = Fernet(self.key)
    #     encrypted_message = f.encrypt(encoded_message)
    #     return encrypted_message
    #
    #     # iv = os.urandom(16)
    #     # ctr = Counter.new(128, initial_value=self.int_of_string(iv))
    #     # aes = AES.new(self.key, AES.MODE_CTR, counter=ctr)
    #     # return (iv + aes.encrypt(plaintext)).hex()
    #
    # def decrypt(self, ciphertext):
    #     f = Fernet(key)
    #     decrypted_message = f.decrypt(ciphertext)
    #
    #     return decrypted_message.decode()
    #
    #     # iv = ciphertext[:16]
    #     # ctr = Counter.new(128, initial_value=self.int_of_string(iv))
    #     # aes = AES.new(self.key, AES.MODE_CTR, counter=ctr)
    #     # return bytes.fromhex(aes.decrypt(ciphertext[16:]))


    # def __init__(self, key, blk_sz):
    #     self.key = key
    #     self.blk_sz = blk_sz
    #
    # def encrypt( self, raw ):
    #     if raw is None or len(raw) == 0:
    #         raise NameError("No value given to encrypt")
    #     raw = raw + '\0' * (self.blk_sz - len(raw) % self.blk_sz)
    #     raw = raw.encode('utf-8')
    #     iv = Random.new().read( AES.block_size )
    #     cipher = AES.new( self.key.encode('utf-8'), AES.MODE_CBC, iv )
    #     return base64.b64encode( iv + cipher.encrypt( raw ) ).decode('utf-8')
    #
    # def decrypt( self, enc ):
    #     if enc is None or len(enc) == 0:
    #         raise NameError("No value given to decrypt")
    #     enc = base64.b64decode(enc)
    #     iv = enc[:16]
    #     cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC, iv )
    #     return re.sub(b'\x00*$', b'', cipher.decrypt( enc[16:])).decode('utf-8')
