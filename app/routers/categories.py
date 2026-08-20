from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.schemas.category import CategoryOut
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await category_service.list_categories(db)
