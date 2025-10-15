revoked_jtis = set()


def add_revoked_jti(jti: str) -> None:
    revoked_jtis.add(jti)


def is_revoked_jti(jti: str) -> bool:
    return jti in revoked_jtis
