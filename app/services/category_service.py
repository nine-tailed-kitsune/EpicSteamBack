from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.category import Category
from app.schemas.category import CreateCategoryRequest

async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.name))
    return list(result.scalars().all())

async def create_category(data: CreateCategoryRequest, db: AsyncSession) -> Category:
    result = await db.execute(select(Category).where(Category.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Категория с таким названием уже существует")

    category = Category(name=data.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

async def delete_category(category_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await db.delete(category)
    await db.commit()
