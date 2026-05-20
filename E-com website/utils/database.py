from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Format: postgresql+asyncpg://user:password@localhost:5432/ecom_db
DATABASE_URL = "postgresql+asyncpg://postgres:invoice_details@localhost:5432/ecomdb"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    from models import product, customer, cart, order, coupon
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

