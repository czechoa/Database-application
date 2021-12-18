from typing import Optional
from app.models.core import DateTimeModelMixin, CoreModel
from app.models.user import UserPublic
from app.models.cleaning import CleaningPublic



class AssessmentBase(CoreModel):
    user_id: Optional[int]
    course_id: Optional[int]
    rating: Optional[int]

class AssessmentCreate(AssessmentBase):
    user_id: int
    course_id: int
    rating:int

class AssessmentUpdate(CoreModel):
    rating: int

class AssessmentInDB(DateTimeModelMixin, AssessmentBase):
    user_id: int
    course_id: int

class AssessmentPublic(AssessmentInDB):
    user: Optional[UserPublic]
    course: Optional[CleaningPublic]
