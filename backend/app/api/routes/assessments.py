from typing import List
from fastapi import APIRouter, Path, Body, status, Depends

from app.api.dependencies.assessments import check_assessment_create_permissions, \
    get_rating_from_path
from app.db.repositories.assessments import AssessmentsRepository
from app.models.assessment import AssessmentInDB, AssessmentCreate
from app.models.course import CourseInDB

from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.courses import get_course_by_id_from_path
from app.models.user import UserInDB

router = APIRouter()


@router.post(
    "/{rating}/",
    response_model=AssessmentInDB,
    name="assessments:create-assessments",
    dependencies=[Depends(check_assessment_create_permissions)],
)
async def create_payment(
        current_user: UserInDB = Depends(get_current_active_user),
        course: CourseInDB = Depends(get_course_by_id_from_path),
        rating: int = Depends(get_rating_from_path),
        assessment_repo: AssessmentsRepository = Depends(get_repository(AssessmentsRepository))
) -> AssessmentInDB:
    new_assessment = AssessmentCreate(user_id = current_user.id, course_id = course.id,rating = rating)
    print('\n'*10)
    print(new_assessment)
    return await assessment_repo.create_assessment_for_course(new_rating= new_assessment)

