import base64
import binascii
import os


def code_decoder(code, decode=False):
    if decode:
        return base64.b64decode(code).decode()
    else:
        return base64.b64encode(f"{code}".encode("utf-8")).decode()


def generate_key(cls):
    return binascii.hexlify(os.urandom(cls)).decode()
