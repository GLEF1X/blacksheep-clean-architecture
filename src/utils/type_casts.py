def bytes_to_string(b: bytes, encoding: str = "utf-8") -> str:
    return str(b, encoding=encoding)


def string_to_bytes(s: str) -> bytes:
    return bytes(s)
