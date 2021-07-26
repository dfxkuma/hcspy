from random import randint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .crypto import Crypto


class KeyPad:
    def __init__(
        self, crypto: Crypto, key_type: str, skip_data: dict, keys: list
    ) -> None:
        if key_type != "number":
            raise TypeError("Only Number")

        self.crypto = crypto
        self.key_type = key_type
        self.skip_data = skip_data
        self.keys = keys

    async def get_geo(self, message: str) -> list:
        geos = []
        for val in list(message):
            if val.isnumeric():
                geos.append(self.keys[self.skip_data.index(val)])
            else:
                raise TypeError("Only Number")
        return geos

    async def geos_encrypt(self, geos: list) -> str:
        out = ""
        for geo in geos:
            x, y = geo

            x_bytes = bytes(map(int, list(x)))
            y_bytes = bytes(map(int, list(y)))
            rand_num = randint(0, 100)

            data = b"%b %b e%c" % (x_bytes, y_bytes, rand_num)

            iv = bytes(
                [
                    0x4D,
                    0x6F,
                    0x62,
                    0x69,
                    0x6C,
                    0x65,
                    0x54,
                    0x72,
                    0x61,
                    0x6E,
                    0x73,
                    0x4B,
                    0x65,
                    0x79,
                    0x31,
                    0x30,
                ]
            )

            out += "$" + self.crypto.seed_encrypt(iv, data).hex(",")
        return out

    async def encrypt_password(self, pw: str) -> str:
        geos = await self.get_geo(pw)
        return await self.geos_encrypt(geos)
