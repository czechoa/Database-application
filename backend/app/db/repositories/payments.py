from typing import List
from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError
from app.db.repositories.base import BaseRepository
from app.models.payment import PaymentCreate, PaymentPublic,PaymentUpdate, PaymentInDB

CREATE_Payment_FOR_CLEANING_QUERY = """
    INSERT INTO user_payment_for_cleanings (course_id, user_id, status)
    VALUES (:course_id, :user_id, :status)
    RETURNING course_id, user_id, status, created_at, updated_at;
"""

class PaymentsRepository(BaseRepository):
    async def create_payment_for_cleaning(self, *, new_payment: PaymentCreate) -> PaymentInDB:
        try:
            created_payment = await self.db.fetch_one(
                query=CREATE_Payment_FOR_CLEANING_QUERY, values={**new_payment.dict(), "status": "pending"}
            )
            return PaymentInDB(**created_payment)
        except UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users aren't allowed create more than one payment  for course.",
            )
