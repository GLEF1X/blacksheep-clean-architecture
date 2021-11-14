from src.utils.password_hashing import hash_password, is_password_verified


def test_hash_password():
    assert isinstance(hash_password("qwerty12345"), str)


def test_verify_password():
    hashed_password = hash_password("qwerty12345")
    assert is_password_verified("qwerty12345", hashed_password) is True
