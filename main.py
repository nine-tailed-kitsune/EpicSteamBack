from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine
from app.models.base import Base
from app.routers import auth, users, games, cart, admin, categories, friends, messages, wishlist, forum, payments, uploads

Path("uploads").mkdir(exist_ok=True)

app = FastAPI(title="Epic Steam API")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.mount("/media", StaticFiles(directory="uploads"), name="media")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(games.router)
app.include_router(cart.router)
app.include_router(admin.router)
app.include_router(categories.router)
app.include_router(friends.router)
app.include_router(messages.router)
app.include_router(wishlist.router)
app.include_router(forum.router)
app.include_router(payments.router)
app.include_router(uploads.router)
