def generate_random_string(length: int = 32) -> str:
    import secrets
    return secrets.token_urlsafe(length)
