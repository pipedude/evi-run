from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, delete, desc, update

from database.models import User, ChatMessage, TokenPrice, KnowledgeVector, Payment
from config import ADMIN_ID, CREDITS_ADMIN_DAILY, CREDITS_USER_DAILY


class UtilsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_token_price(self, price: float):
        token = await self.session.scalar(select(TokenPrice).where(TokenPrice.token == 'sol'))

        if token:
            token.price_usd = price
        else:
            token = TokenPrice(token='sol', price_usd=price)
            self.session.add(token)

        await self.session.commit()

    async def get_token(self):
        token = await self.session.scalar(select(TokenPrice).where(TokenPrice.token == 'sol'))
        return token

    async def get_knowledge_vectore_store_id(self):
        return await self.session.scalar(select(KnowledgeVector))

    async def add_knowledge_vectore_store_id(self, vectore_store_id):
        vectore_store = KnowledgeVector(id_vector=vectore_store_id)
        self.session.add(vectore_store)
        await self.session.commit()

    async def delete_knowledge_vectore_store_id(self):
        await self.session.execute(delete(KnowledgeVector))
        await self.session.commit()

    async def check_payment_suffix(self, suffix: str):
        payment = await self.session.scalar(select(Payment).
                                            where(Payment.random_suffix == suffix).
                                            order_by(desc(Payment.created_at)).limit(1))
        if payment:
            now_utc = datetime.now(timezone.utc)
            created_utc = payment.created_at.astimezone(timezone.utc)
            if (now_utc - created_utc) >= timedelta(minutes=15):
                return True
            return False

        return True

    async def get_payment(self, payment_id: int) -> Payment:
        payment = await self.session.scalar(select(Payment).where(Payment.id == payment_id))
        return payment

    async def update_payment_status(self, payment_id: int, status: str):
        await self.session.execute(update(Payment).where(Payment.id == payment_id).values(status=status))
        await self.session.commit()

    async def update_tokens_daily(self):
        await self.session.execute(update(User).where(and_(User.telegram_id != ADMIN_ID,
                                                           User.balance_credits < CREDITS_USER_DAILY)
                                                      ).values(balance_credits=CREDITS_USER_DAILY))
        await self.session.execute(update(User).where(and_(User.telegram_id == ADMIN_ID,
                                                           User.balance_credits < CREDITS_USER_DAILY)
                                                      ).values(balance_credits=CREDITS_ADMIN_DAILY))
        await self.session.commit()