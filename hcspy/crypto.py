import hashlib
import hmac
import os
from base64 import b64decode

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA

from .seed import SEED


class Crypto:
    def __init__(self) -> None:
        self.uuid = os.urandom(int(32)).hex()
        self.gen_session_key = os.urandom(int(8)).hex()
        self.key = None
        self.session_key = [int(i, 16) for i in list(self.gen_session_key)]

    @staticmethod
    async def _pad(txt) -> bytes:
        if len(txt) < 16:
            txt += b"\x00" * (16 - len(txt))
        return txt

    async def rsa_encrypt(self, data: bytes) -> hex:
        cipher = PKCS1_OAEP.new(key=self.key, hashAlgo=SHA1)
        return cipher.encrypt(data).hex()

    async def get_encrypted_key(self) -> hex:
        return await self.rsa_encrypt(self.gen_session_key.encode())

    async def hmac_digest(self, msg: bytes) -> hex:
        return hmac.new(
            msg=msg, key=self.gen_session_key.encode(), digestmod=hashlib.sha256
        ).hexdigest()

    async def seed_encrypt(self, iv, data) -> bytes:
        s = SEED()
        round_key = await s.seed_round_key(bytes(self.session_key))
        return await s.my_cbc_encrypt(await self._pad(data), round_key, iv)

    async def set_pub_key(self, b64: str) -> None:
        data = b64decode(b64)
        self.key = RSA.import_key(data)
