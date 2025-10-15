from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from sqlalchemy import select, update


async def create_user(db: AsyncSession, name: str, last_name: str, father_name: str, email: str,
                      hashed_passwd: str) -> User:
    user = User(name=name, father_name=father_name, last_name=last_name, email=email, passwd=hashed_passwd)
    db.add(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User:

    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one()
    return user




async def get_user_by_id(db: AsyncSession, id: int) -> User:
    res = await db.execute(select(User).where(User.id == id))
    user = res.scalar_one()
    return user

async def delete_user_by_id(db: AsyncSession, user_id: int) -> None:
    res = await db.execute(
        update(User).where(User.id == user_id).values(is_active=False).returning(User.id, User.is_active))
    await db.commit()
    print(f"{res.fetchall()=}")

async def update_user_by_id(db: AsyncSession, user_id: int, values: dict) -> User:
    res = await db.execute(
        update(User).where(User.id == user_id).values(**values).returning(User))

    user = res.scalars().first()
    await db.commit()
    print(f"{user=}")
    return user
