from typing import List
from fastapi import APIRouter, Path, Body, status, Depends

from app.api.dependencies.cleanings import get_cleaning_by_id_from_path
from app.models.cleaning import CleaningInDB
from app.models.course import CourseInDB
from app.models.payment import PaymentCreate, PaymentUpdate, PaymentInDB, PaymentPublic
from app.api.dependencies.payments import (
    check_payment_create_permissions,
    check_payment_list_permissions,
    check_payment_get_permissions,
    list_payments_for_course_by_id_from_path,
    # get_payment_for_course_from_user_by_path
)
from app.db.repositories.payments import PaymentsRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.courses import get_course_by_id_from_path
from app.models.user import UserInDB

router = APIRouter()


@router.post(
    "/",
    response_model=PaymentPublic,
    name="payments:create-payment",
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_payment_create_permissions)],
)
async def create_payment(
    # course: CourseInDB = Depends(get_course_by_id_from_path()),
    # cleaning: CleaningInDB = Depends(get_cleaning_by_id_from_path),
    current_user: UserInDB = Depends(get_current_active_user),
    payments_repo: PaymentsRepository = Depends(get_repository(PaymentsRepository)),
) -> PaymentPublic:
    course: CourseInDB = Depends(get_course_by_id_from_path()),
    return await payments_repo.create_payment_for_course(
        new_offer=PaymentCreate(course_id=course.id, user_id=current_user.id)
    )


# @router.get(
#     "/",
#     response_model=List[PaymentPublic],
#     name="offers:list-offers-for-cleaning",
#     dependencies=[Depends(check_payment_list_permissions())],
# )
# async def list_offers_for_course(
#         payments: List[PaymentInDB] = Depends(list_payments_for_course_by_id_from_path())
# ) -> List[PaymentPublic]:
#     return payments


# @router.get(
#     "/{username}/",
#     response_model=PaymentPublic,
#     name="offers:get-offer-from-user",
#     dependencies=[Depends(check_payment_get_permissions())],
# )
# async def get_offer_from_user(payments: PaymentInDB = Depends(get_payment_for_course_from_user_by_path())) -> PaymentPublic:
#     return payments
#

# @router.put("/{username}/", response_model=PaymentPublic, name="payments:accept-payment-from-user")
# async def accept_payment_from_user(username: str = Path(..., min_length=3)) -> PaymentPublic:
#     return None
#
#
# @router.put("/", response_model=PaymentPublic, name="payments:cancel-payment-from-user")
# async def cancel_payment_from_user() -> PaymentPublic:
#     return None
#
#
# @router.delete("/", response_model=int, name="payments:rescind-payment-from-user")
# async def rescind_payment_from_user() -> PaymentPublic:
#     return None
