import secrets


def generate_session_id(length=16):
    session_id = secrets.token_hex(length)
    return session_id
