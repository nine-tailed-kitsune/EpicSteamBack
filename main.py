from fastapi import FastAPI
from database import engine
from app.models.base import Base
from app.routers import auth, users, games, cart, admin

app = FastAPI(title="Steam API")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(games.router)
app.include_router(cart.router)
app.include_router(admin.router)