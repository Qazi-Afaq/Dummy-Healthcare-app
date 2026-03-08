from werkzeug.security import (check_password_hash, generate_password_hash)


def test_password_hashing():
    password = "SecurePass1"
    hashed = generate_password_hash(password)
    assert hashed != password
    assert check_password_hash(hashed, password) is True
    assert check_password_hash(hashed, "WrongPass1") is False
