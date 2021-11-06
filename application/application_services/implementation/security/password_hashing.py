import bcrypt


def get_hashed_password(plain_text_password: str):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def is_password_verified(plain_text_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_text_password, hashed_password)
