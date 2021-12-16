from typing import List
from fastapi import HTTPException, Depends, status
from app.models.user import UserInDB
from app.models.course import CourseInDB
from app.models.payment  import PaymentInDB
from app.db.repositories.payments import PaymentsRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.users import get_user_by_username_from_path
from app.api.dependencies.courses import get_course_by_id_from_path


async def get_payment_for_course_from_user(
    *, user: UserInDB, course: CourseInDB, payments_repo: PaymentsRepository,
) -> PaymentInDB:
    payment = await payments_repo.get_payment_for_course_from_user(course=course, user=user)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    return payment

# async def get_payments_user(
#     *, user: UserInDB, course: CourseInDB, payments_repo: PaymentsRepository,
# ) -> PaymentInDB:
#     payment = await payments_repo.get_payment_for_course_from_user(course=course, user=user)
#     if not payment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
#     return payment


async def get_payment_for_course_from_user_by_path(
    user: UserInDB = Depends(get_user_by_username_from_path),
    course: CourseInDB = Depends(get_course_by_id_from_path),
    payments_repo: PaymentsRepository = Depends(get_repository(PaymentsRepository)),
) -> PaymentInDB:
    return await get_payment_for_course_from_user(user=user, course=course, payments_repo=payments_repo)

async def list_payments_for_course_by_id_from_path(
    course: CourseInDB = Depends(get_course_by_id_from_path),
    payments_repo: PaymentsRepository = Depends(get_repository(PaymentsRepository)),
) -> List[PaymentInDB]:
    return await payments_repo.list_payments_for_course(course=course)

async def check_payment_create_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    course: CourseInDB = Depends(get_course_by_id_from_path),
    payments_repo: PaymentsRepository = Depends(get_repository(PaymentsRepository)),
) -> None:
    if course.owner == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are unable to create payments for course jobs they own.",
        )
    if await payments_repo.get_payment_for_course_from_user(course=course, user=current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users aren't allowed create more than one payment for a course job.",
        )

def check_payment_list_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    course: CourseInDB = Depends(get_course_by_id_from_path),
) -> None:

    if course.owner != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unable to access payments.",

        )

def check_payment_get_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    course: CourseInDB = Depends(get_course_by_id_from_path),
    payment: PaymentInDB = Depends(get_payment_for_course_from_user_by_path),
) -> None:
    if course.owner != current_user.id and payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unable to access payment.",
        )

def check_offer_acceptance_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    course: CourseInDB = Depends(get_course_by_id_from_path),
    payment: PaymentInDB = Depends(get_payment_for_course_from_user_by_path),
    existing_offers: List[PaymentInDB] = Depends(list_payments_for_course_by_id_from_path)
) -> None:
    if course.owner != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner of the course may accept offers."
        )
    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only accept payments that are currently pending."
        )

    if "accepted" in [o.status for o in existing_offers]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="That course already has an accepted offer."
        )
