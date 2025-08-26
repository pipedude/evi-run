import os

from dotenv import load_dotenv

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Table, BigInteger,
    TIMESTAMP, func
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config import START_BALANCE

load_dotenv()

# Create SQLAlchemy base
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    os.getenv('DATABASE_URL'),
    echo=False,
)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(BigInteger, primary_key=True)
    language = Column(String(10), nullable=True)
    balance_credits = Column(Float, default=START_BALANCE)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    wallets = relationship('Wallet', back_populates='user')
    messages = relationship('ChatMessage', back_populates='user')
    payments = relationship('Payment', back_populates='user')
    memory = relationship('MemoryVector', back_populates='user')
    logs = relationship('Logs', back_populates='user')


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='messages')


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)

    user_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    amount_usd = Column(Integer, nullable=False)
    crypto_amount = Column(String)
    crypto_currency = Column(String(20))  # 'TON', 'EVI'
    random_suffix = Column(String(10), nullable=False)
    status = Column(String(20), default='pending')  # pending, confirmed, failed
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    confirmed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user = relationship('User', back_populates='payments')


class TokenPrice(Base):
    __tablename__ = 'token_prices'

    id = Column(Integer, primary_key=True)
    token = Column(String(20), unique=True)
    price_usd = Column(Float, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), server_onupdate=func.now())


class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    encrypted_private_key = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='wallets')


class KnowledgeVector(Base):
    __tablename__ = 'knowledge_vectors'

    id = Column(Integer, primary_key=True)
    id_vector = Column(Text, nullable=False)
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class MemoryVector(Base):
    __tablename__ = 'memory_vectors'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    id_vector = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='memory')


class Logs(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='logs')


class UserTasks(Base):
    __tablename__ = 'user_tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    description = Column(Text, nullable=False)
    agent_message = Column(Text, nullable=False)
    schedule_type = Column(String('20'), nullable=False)
    time_str = Column(Text, nullable=True)
    date_str = Column(Text, nullable=True)
    interval_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_executed = Column(TIMESTAMP(timezone=True), server_onupdate=func.now(), nullable=True)





async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
