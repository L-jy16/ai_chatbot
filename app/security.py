import bcrypt

# bcrypt는 72바이트까지만 처리한다. bcrypt 5는 넘는 입력에 ValueError를 던진다.
MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱한다. 72바이트 초과 입력은 호출 전에 막아야 한다."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """비밀번호가 해시와 맞는지 확인한다. 72바이트 초과는 가입될 수 없으므로 불일치로 본다."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))
