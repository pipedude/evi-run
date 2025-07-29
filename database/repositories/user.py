import base64

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, delete, update, asc

from database.models import User, ChatMessage, Wallet, MemoryVector, Payment


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int):
        return await self.session.get(User, telegram_id)

    async def create_if_not_exists(self, telegram_id: int, **kwargs):
        user = await self.get_by_telegram_id(telegram_id)

        if not user:
            user = User(telegram_id=telegram_id, **kwargs)
            self.session.add(user)
            await self.session.commit()

        return user

    async def update(self, user: User, **kwargs):
        if 'balance_credits' in kwargs:
            kwargs['balance_credits'] = user.balance_credits - kwargs['balance_credits']

        await self.session.execute(
            update(User).where(User.telegram_id == user.telegram_id).values(**kwargs)
        )

        await self.session.commit()

    async def delete_chat_messages(self, user: User):
        await self.session.execute(delete(ChatMessage).where(ChatMessage.user_id == user.telegram_id))

        await self.session.commit()

    async def get_wallet(self, user_id: int):
        wallet = await self.session.scalar(select(Wallet.encrypted_private_key).where(Wallet.user_id == user_id))
        if wallet:
            base64_bytes = wallet.encode('utf-8')
            text_bytes = base64.b64decode(base64_bytes)
            text = text_bytes.decode('utf-8')
            return text
        return None

    async def get_messags(self, user_id: int):
        return (await self.session.scalars(select(ChatMessage).
                                           where(ChatMessage.user_id == user_id).
                                           order_by(asc(ChatMessage.id)
                                                    )
                                           )
                ).fetchall()

    async def get_memory_vector(self, user_id: int):
        return await self.session.scalar(select(MemoryVector).where(MemoryVector.user_id == user_id))

    async def add_memory_vector(self, user_id: int, vector_store_id: int):
        memory_vector = MemoryVector(user_id=user_id, id_vector=vector_store_id)
        self.session.add(memory_vector)
        await self.session.commit()

    async def delete_memory_vector(self, user_id: int):
        await self.session.execute(delete(MemoryVector).where(MemoryVector.user_id == user_id))
        await self.session.commit()

    async def add_context(self, user_id: int, role: str, content: str):
        chat_message = ChatMessage(user_id=user_id, role=role, content=content)
        self.session.add(chat_message)
        await self.session.commit()
        return chat_message.id

    async def delete_wallet_key(self, user_id: int):
        await self.session.execute(delete(Wallet).where(Wallet.user_id == user_id))
        await self.session.commit()

    async def add_wallet_key(self, user_id: int, key: str):
        await self.delete_wallet_key(user_id=user_id)
        text_bytes = key.encode('utf-8')
        base64_bytes = base64.b64encode(text_bytes)
        base64_string = base64_bytes.decode('utf-8')
        wallet = Wallet(user_id=user_id, encrypted_private_key=base64_string)
        self.session.add(wallet)
        await self.session.commit()

    async def add_payment(self, user_id: int, amount: int, crypto_amount: str,
                          crypto_currency: str, random_suffix: str):
        payment = Payment(user_id=user_id, amount_usd=amount, crypto_amount=crypto_amount,
                          crypto_currency=crypto_currency, random_suffix=random_suffix)
        self.session.add(payment)
        await self.session.commit()
        return payment.id

    async def add_user_credits(self, user_id: int, balance_credits: int):
        await self.session.execute(update(User).where(User.telegram_id == user_id).
                                   values(balance_credits=User.balance_credits + balance_credits))
        await self.session.commit()

    async def get_row_for_md(self, row_id: int):
        return await self.session.scalar(select(ChatMessage).where(ChatMessage.id == row_id))
