from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.auth import hash_password, verify_password, create_access_token, is_currently_banned

async def register_user(data: RegisterRequest, db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(
            (User.username == data.username) | (User.email == data.email)
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        if existing.username == data.username:
            raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
        raise HTTPException(status_code=400, detail="Email уже занят")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def login_user(username: str, password: str, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    if is_currently_banned(user):
        raise HTTPException(status_code=403, detail="Вы заблокированы и не можете войти")

    return TokenResponse(access_token=create_access_token(user.id))