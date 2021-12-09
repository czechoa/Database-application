from typing import Optional, Union
from app.models.core import IDModelMixin, DateTimeModelMixin, CoreModel


class SkillBase(CoreModel):
    """
    All common characteristics of our Course resource
    """
    name: Optional[str]

class SkillCreate(SkillBase):
    name: str

class SkillConnectionPublic(SkillBase):
    name: str

class SkillConnection(SkillConnectionPublic):
    id_course: int

class SkillInDB(IDModelMixin, SkillBase):
    name: str

class SkillConnectionINDB(IDModelMixin):
    id_course:int
    id_skill:int


class SkillPublic(SkillInDB):
    # owner: Union[int, UserPublic]
    name: str
