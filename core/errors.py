class AuthError(Exception):
    pass


class InvalidCredentials(AuthError):
    pass


class UserBlocked(AuthError):
    pass
