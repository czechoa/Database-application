from typing import List
from fastapi import HTTPException, Depends, status, Path

from app.api.dependencies.payments import get_payment_for_course_from_user, get_payment_for_course_from_user_by_path
from app.db.repositories.payments import PaymentsRepository
from app.models.user import UserInDB
from app.models.course import CourseInDB
from app.models.payment  import PaymentInDB
from app.db.repositories.assessments import AssessmentsRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.users import get_user_by_username_from_path
from app.api.dependencies.courses import get_course_by_id_from_path

async def check_assessment_create_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    course: CourseInDB = Depends(get_course_by_id_from_path),
    assessment_repo: AssessmentsRepository = Depends(get_repository(AssessmentsRepository)),
    payments_repo: PaymentsRepository = Depends(get_repository(PaymentsRepository)),

) -> None:
    if course.owner == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are unable to assessment for course they own.",
        )
    if await assessment_repo.get_assessment_for_course_from_user(course=course, user=current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users aren't allowed create more than one assessment for a course.",
        )
    payment = await payments_repo.get_payment_for_course_from_user(course=course, user=current_user)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found,user have to buy course to  do an evaluation.")


async def get_rating_from_path(
    rating: int = Path(..., ge=1)
) -> None:
    if rating < 0 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="evaluation should have value between 1-5",
        )
    print('get_rating_from_path  ',rating)
    return rating


