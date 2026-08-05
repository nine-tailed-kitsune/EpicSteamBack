from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.comment import ProfileComment
from app.schemas.user import UpdateProfileRequest
from app.schemas.comment import ProfileCommentOut, AddCommentRequest
from app.auth import hash_password

async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

async def update_profile(
    data: UpdateProfileRequest,
    current_user: User,
    db: AsyncSession
) -> User:
    if data.username is not None:
        result = await db.execute(
            select(User).where(User.username == data.username, User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
        current_user.username = data.username

    if data.email is not None:
        result = await db.execute(
            select(User).where(User.email == data.email, User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email уже занят")
        current_user.email = data.email

    if data.password is not None:
        if len(data.password) < 6:
            raise HTTPException(status_code=400, detail="Пароль должен быть не короче 6 символов")
        current_user.hashed_password = hash_password(data.password)

    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url

    if data.background_url is not None:
        current_user.background_url = data.background_url

    await db.commit()
    await db.refresh(current_user)
    return current_user

async def get_profile_comments(user_id: int, db: AsyncSession) -> list[ProfileCommentOut]:
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    result = await db.execute(
        select(ProfileComment)
        .where(ProfileComment.profile_owner_id == user_id)
        .options(selectinload(ProfileComment.author))
        .order_by(ProfileComment.created_at.desc())
    )
    comments = result.scalars().all()

    return [
        ProfileCommentOut(
            id=c.id,
            author_id=c.author_id,
            author_username=c.author.username,
            text=c.text,
            created_at=c.created_at
        )
        for c in comments
    ]

async def add_profile_comment(
    user_id: int,
    data: AddCommentRequest,
    current_user: User,
    db: AsyncSession
) -> ProfileCommentOut:
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    comment = ProfileComment(
        profile_owner_id=user_id,
        author_id=current_user.id,
        text=data.text
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return ProfileCommentOut(
        id=comment.id,
        author_id=comment.author_id,
        author_username=current_user.username,
        text=comment.text,
        created_at=comment.created_at
    )

async def delete_profile_comment(
    user_id: int,
    comment_id: int,
    current_user: User,
    db: AsyncSession
) -> None:
    result = await db.execute(
        select(ProfileComment).where(
            ProfileComment.id == comment_id,
            ProfileComment.profile_owner_id == user_id
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")

    await db.delete(comment)
    await db.commit()