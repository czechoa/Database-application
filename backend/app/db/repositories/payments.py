from typing import List
from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError
from app.db.repositories.base import BaseRepository
from app.models.course import CourseInDB
from app.models.payment import PaymentCreate, PaymentPublic,PaymentUpdate, PaymentInDB
from app.models.user import UserInDB

CREATE_PAYMENT_FOR_COURSE_QUERY = """
    INSERT INTO payments(course_id, user_id, status)
    VALUES (:course_id, :user_id, :status)
    RETURNING course_id, user_id, status, created_at, updated_at;
"""

# LIST_PAYMENTS_FOR_COURSE_QUERY = """
#     select *
#     from payments
#     where course_id = :course_id;
# """
#
GET_PAYMENT_FOR_COURSE_FROM_USER_QUERY = """
    select *
    from payments
    where course_id = :course_id and  user_id = :user_id;
"""

GET_USER_PAYMENTS_QUERY = """
    select *
    from payments
    where course_id = :course_id and  user_id = :user_id;
"""

GET_USER_PAYMENTS_QUERY = """
    select p.*
    from payments p 
    join users u on u.id = p.user_id
    where u.id = :user_id;
"""

# ACCEPT_OFFER_QUERY = """
#     UPDATE payments
#     SET status = 'accepted'
#     WHERE course_id = :course_id AND user_id = :user_id
#     RETURNING *;
# """
#
# REJECT_ALL_OTHER_OFFERS_QUERY = """
#     UPDATE payments
#     SET status = 'rejected'
#     WHERE course_id = :course_id
#     AND user_id != :user_id
#     AND status = 'pending';
# """


class PaymentsRepository(BaseRepository):

    async def create_payment_for_course(self, *, new_payment: PaymentCreate) -> PaymentInDB:
        try:
            created_payment = await self.db.fetch_one(
                query=CREATE_PAYMENT_FOR_COURSE_QUERY, values={**new_payment.dict(), "status": "pending"}
            )
            return PaymentInDB(**created_payment)
        except UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users aren't allowed create more than one payment for course.",
            )

    # async def list_payments_for_course(self, *, course: CourseInDB) -> List[PaymentInDB]:
    #     offers = await self.db.fetch_all(
    #         query=LIST_PAYMENTS_FOR_COURSE_QUERY,
    #         values={"course_id": course.id}
    #     )
    #     return [PaymentInDB(**o) for o in offers]


    async def list_user_payments(self, *, user: UserInDB) ->CourseInDB:
        print('\n'*10)
        return None
        # print("\n" * 10)
        # print("ala ma kota, i to dwa ")
        #
        # offers = await self.db.fetch_all(
        #     query=GET_USER_PAYMENTS_QUERY,
        #     values={"user_id": user.id}
        # )
        # print([PaymentInDB(**o) for o in offers])
        #
        # return [PaymentInDB(**o) for o in offers]

    async def get_payment_for_course_from_user(self, *, course: CourseInDB, user: UserInDB) -> PaymentInDB:
        offer_record = await self.db.fetch_one(
            query=GET_PAYMENT_FOR_COURSE_FROM_USER_QUERY,
            values={"course_id": course.id, "user_id": user.id},
        )
        if not offer_record:
            return None
        return PaymentInDB(**offer_record)


    # async def accept_offer(self, *, payment: PaymentInDB, payment_update: PaymentUpdate) -> PaymentInDB:
    #     async with self.db.transaction():
    #         accepted_offer = await self.db.fetch_one(
    #             query=ACCEPT_OFFER_QUERY,  # accept current offer
    #             values={"course_id": payment.cleaning_id, "user_id": payment.user_id},
    #         )
    #         await self.db.execute(
    #             query=REJECT_ALL_OTHER_OFFERS_QUERY,  # reject all other offers
    #             values={"payment_id": payment.cleaning_id, "user_id": payment.user_id},
    #         )
    #         return PaymentInDB(**accepted_offer)
