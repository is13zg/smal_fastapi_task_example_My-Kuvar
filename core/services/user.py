from sqlalchemy.ext.asyncio import AsyncSession
from core.security import make_hash, check_hash, gen_token, decode_token
from core.repository.user import create_user, get_user_by_email, get_user_by_id, delete_user_by_id, update_user_by_id
from core.repository.jwt import is_revoked_jti, add_revoked_jti
from core.errors import InvalidCredentials, UserBlocked
from sqlalchemy.exc import NoResultFound
from models.user import User
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends
from db.session import get_session
from fastapi import HTTPException
from typing import Tuple

security = HTTPBearer(auto_error=False)


async def auth_user(cred: HTTPAuthorizationCredentials | None = Depends(security),
                    db: AsyncSession = Depends(get_session)) -> Tuple[User, str]:
    if not cred or cred.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Need bearer")

    try:
        paylod = decode_token(cred.credentials)
        user_id = int(paylod['sub'])
    except Exception:
        raise HTTPException(status_code=401, detail="No correct token")

    if is_revoked_jti(paylod['jti']):
        raise HTTPException(status_code=401, detail="No correct token")

    user = await get_user_by_id(db, int(user_id))

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="No find user")

    return user, paylod['jti']


async def register(db: AsyncSession, name: str, last_name: str, father_name: str, email: str,
                   passwd: str) -> User:
    hash_passwd = make_hash(passwd)
    user = await create_user(db, name, last_name, father_name, email, hash_passwd)

    await db.commit()
    return user


async def login(db: AsyncSession, email: str,
                passwd: str) -> str:
    try:
        user = await get_user_by_email(db, email)
    except NoResultFound:
        raise InvalidCredentials

    if not check_hash(passwd, user.passwd):
        raise InvalidCredentials
    print(f"{user=}")

    if not user.is_active:
        raise UserBlocked

    return gen_token(user.id)


def logout(jti: str) -> None:
    add_revoked_jti(jti)


async def delete(user_id: int, jti: str, db: AsyncSession) -> None:
    logout(jti)
    await delete_user_by_id(db, user_id)


async def update(user_id: int, db: AsyncSession, values: dict) -> User:
    if "passwd" in values.keys():
        values["passwd"] = make_hash(values["passwd"])

    res = await update_user_by_id(db, user_id, values)
    print(f"{values=}")
    print(f"{res=}")
    return res
