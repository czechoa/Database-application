from app.db.repositories.base import BaseRepository
from app.models.assessment import AssessmentInDB, AssessmentCreate
from app.models.course import CourseInDB
from app.models.user import UserInDB
from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError

GET_ASSESSMENT_FOR_COURSE_FROM_USER_QUERY = """
    select *
    from assessments
    where course_id = :course_id and  user_id = :user_id;
"""
CREATE_PAYMENT_FOR_COURSE_QUERY = """
    INSERT INTO assessments(course_id, user_id, rating)
    VALUES (:course_id, :user_id, :rating)
    RETURNING *;
"""

class AssessmentsRepository(BaseRepository):

    async def create_assessment_for_course(self, *, new_rating: AssessmentCreate) -> AssessmentInDB:
        try:
            created_payment = await self.db.fetch_one(
                query=CREATE_PAYMENT_FOR_COURSE_QUERY, values={**new_rating.dict()}
            )
            return AssessmentInDB(**created_payment)
        except UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users aren't allowed create more than one payment for course.",
            )



    async def get_assessment_for_course_from_user(self, *, course: CourseInDB, user: UserInDB) -> AssessmentInDB:
        offer_record = await self.db.fetch_one(
            query=GET_ASSESSMENT_FOR_COURSE_FROM_USER_QUERY,
            values={"course_id": course.id, "user_id": user.id},
        )
        if not offer_record:
            return None
        return AssessmentInDB(**offer_record)
