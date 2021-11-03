from app.models.user import UserPublic
from typing import Optional, Union
from app.models.core import IDModelMixin, DateTimeModelMixin, CoreModel


class CourseBase(CoreModel):
    """
    All common characteristics of our Course resource
    """
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]

class CourseCreate(CourseBase):
    name: str
    price: float

class CourseInDB(IDModelMixin, DateTimeModelMixin, CourseBase):
    name: str
    price: float
    owner: int

class CoursePublic(CourseInDB):
    owner: Union[int, UserPublic]
