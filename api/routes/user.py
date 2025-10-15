from fastapi import APIRouter, Depends
from schemas.user import UserRegister, UserOut, UserLogin, TokenOut, UserUpdate, ExtUserOut
from db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from core.services.user import register, login, auth_user, logout, delete, update
from core.errors import InvalidCredentials, UserBlocked
from models.user import User
from typing import Tuple

user_router = APIRouter(prefix="/user", tags=["Work with user", ])


@user_router.post("/register")
async def register_user(get_user: UserRegister, db: AsyncSession = Depends(get_session)) -> UserOut:
    try:
        db_user = await register(db, **get_user.model_dump(exclude={'rep_passwd'}))

    except IntegrityError as e:
        is_unique_violation = (
                isinstance(getattr(e, "orig", None), UniqueViolationError)
                or getattr(getattr(e, "orig", None), "sqlstate", None) == "23505"
        )
        if is_unique_violation:
            raise HTTPException(status_code=409, detail="Email already registered.")

        raise HTTPException(status_code=500, detail="Database error.")
    return UserOut(id=db_user.id, name=db_user.name)


@user_router.post("/login")
async def login_user(user_login: UserLogin, db: AsyncSession = Depends(get_session)) -> TokenOut:
    try:
        token = await login(db, user_login.email, user_login.passwd)
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="No correct user or password")
    except UserBlocked:
        raise HTTPException(status_code=403, detail="User blocked")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Login error")

    return TokenOut(access_token=token)


@user_router.get("/me")
async def logout_user(auth: Tuple[User, str] = Depends(auth_user)) -> ExtUserOut:
    user, jti = auth
    return ExtUserOut(id=user.id, name=user.name, email=user.email, last_name=user.last_name,
                      father_name=user.father_name)


@user_router.post("/logout")
async def logout_user(auth: Tuple[User, str] = Depends(auth_user)) -> dict:
    user, jti = auth
    logout(jti)

    return {"message": f"user {user.id=} logout", "status": "ok"}


@user_router.post("/update")
async def update_user(user_update: UserUpdate, auth: Tuple[User, str] = Depends(auth_user),
                      db: AsyncSession = Depends(get_session)) -> UserOut:
    user, jti = auth
    try:
        new_user = await update(user.id, db, user_update.model_dump(exclude_unset=True, exclude={"rep_passwd"}))

    except IntegrityError as e:
        is_unique_violation = (
                isinstance(getattr(e, "orig", None), UniqueViolationError)
                or getattr(getattr(e, "orig", None), "sqlstate", None) == "23505"
        )
        if is_unique_violation:
            raise HTTPException(status_code=409, detail="Email already registered.")

        raise HTTPException(status_code=500, detail="Database error.")
    return UserOut(id=new_user.id, name=new_user.name)


@user_router.delete("/delete")
async def delete_user(auth: Tuple[User, str] = Depends(auth_user), db: AsyncSession = Depends(get_session)) -> dict:
    user, jti = auth
    await delete(user.id, jti, db)

    return {"message": f"user {user.id=} logout and delete", "status": "ok"}
