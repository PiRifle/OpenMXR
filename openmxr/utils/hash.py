import hashlib


def mkmd5(string: str):
    return hashlib.md5(string.encode()).hexdigest()
