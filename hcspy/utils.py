from base64 import b64decode, b64encode
from typing import Dict, List, Optional, Any
import types
import functools
import jwt
import random

from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher.PKCS1_v1_5 import PKCS115_Cipher
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey


def encrypt_login(content: str) -> str:
    pubkey: str = (
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA81dCnCKt0NVH7j5Oh2"
        "+SGgEU0aqi5u6sYXemouJWXOlZO3jqDsHYM1qfEjVvCOmeoMNFXYSXdNhflU7mjWP8jWUmkYIQ8o3FGqMzsMTNxr"
        "+bAp0cULWu9eYmycjJwWIxxB7vUwvpEUNicgW7v5nCwmF5HS33Hmn7yDzcfjfBs99K5xJEppHG0qc"
        "+q3YXxxPpwZNIRFn0Wtxt0Muh1U8avvWyw03uQ/wMBnzhwUC8T4G5NclLEWzOQExbQ4oDlZBv8BM"
        "/WxxuOyu0I8bDUDdutJOfREYRZBlazFHvRKNNQQD2qDfjRz484uFs7b5nykjaMB9k/EJAuHjJzGs9MMMWtQIDAQAB== "
    )
    rsa_public_key: bytes = b64decode(pubkey)
    pub_key: RsaKey = RSA.importKey(rsa_public_key)
    cipher: PKCS115_Cipher = PKCS1_v1_5.new(pub_key)
    msg: bytes = content.encode("utf-8")
    length = 245
    msg_list: List[bytes] = [
        msg[i : i + length] for i in list(range(0, len(msg), length))
    ]
    encrypt_msg_list: List[bytes] = [
        b64encode(cipher.encrypt(message=msg_str)) for msg_str in msg_list
    ]
    return encrypt_msg_list[0].decode("utf-8")


def multi_finder(
    data: Dict[str, List[str]], keyword: Optional[str], prefix: str
) -> Optional[str]:
    for key, value in data.items():
        if keyword in value:
            return key.replace(prefix, "")
    return None


def url_create_with(url: str, **query: Any) -> str:
    _url: str = url + "?"
    for q, v in query.items():
        if v is not None:
            _url += f"{q}={v}&"
    return _url[:-1]


def copy_function(function):
    g = types.FunctionType(
        function.__code__,
        function.__globals__,
        name=function.__name__,
        argdefs=function.__defaults__,
        closure=function.__closure__,
    )
    g = functools.update_wrapper(g, function)
    g.__kwdefaults__ = function.__kwdefaults__
    return g


def duplicate(*aliases):
    def decorator(function):
        new_function = copy_function(function)
        new_function.__doc__ = "Duplicate for :meth:`{0.__name__}`.".format(function)
        function._aliases = {a: new_function for a in aliases}
        return function

    return decorator


def duplicated(cls):
    original_methods = cls.__dict__.copy()
    for method in original_methods.values():
        if hasattr(method, "_aliases"):
            for name, func in method._aliases.items():
                if name in original_methods.keys():
                    raise ValueError(
                        "{} already existed in {}, "
                        "cannot create alias.".format(name, cls.__name__)
                    )
                setattr(cls, name, func)
    return cls


def generate_secret_key(length: int = 300) -> str:
    return hex(random.getrandbits(length))


def encode_data(data: dict, key: str) -> str:
    return str(jwt.encode(data, key, algorithm="HS256"))


def decode_data(string: str, key: str) -> dict:
    return jwt.decode(string, key, algorithms=["HS256"])
