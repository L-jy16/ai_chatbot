from app.security import MAX_PASSWORD_BYTES, hash_password, verify_password


def test_hash_is_bcrypt_not_plaintext():
    hashed = hash_password("shorts1234")
    assert hashed != "shorts1234"
    assert hashed.startswith("$2b$")
    assert len(hashed) == 60


def test_same_password_gets_different_salt():
    assert hash_password("shorts1234") != hash_password("shorts1234")


def test_verify_password_matches_only_original():
    hashed = hash_password("shorts1234")
    assert verify_password("shorts1234", hashed) is True
    assert verify_password("shorts12345", hashed) is False


def test_verify_password_handles_korean_password():
    hashed = hash_password("경제숏폼최고야")
    assert verify_password("경제숏폼최고야", hashed) is True


def test_verify_password_rejects_over_72_bytes_without_error():
    hashed = hash_password("a" * MAX_PASSWORD_BYTES)
    assert verify_password("a" * (MAX_PASSWORD_BYTES + 1), hashed) is False
