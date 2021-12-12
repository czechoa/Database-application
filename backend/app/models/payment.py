from typing import Optional
from enum import Enum
from app.models.core import DateTimeModelMixin, CoreModel
from app.models.user import UserPublic
from app.models.cleaning import CleaningPublic

class PaymentStatus(str, Enum):
    accepted = "accepted"
    rejected = "rejected"
    pending = "pending"
    cancelled = "cancelled"

class PaymentBase(CoreModel):
    user_id: Optional[int]
    course_id: Optional[int]
    status: Optional[PaymentStatus] = PaymentStatus.pending

class PaymentCreate(PaymentBase):
    user_id: int
    course_id: int

class PaymentUpdate(CoreModel):
    status: PaymentStatus

class PaymentInDB(DateTimeModelMixin, PaymentBase):
    user_id: int
    course_id: int

class PaymentPublic(PaymentInDB):
    user: Optional[UserPublic]
    course: Optional[CleaningPublic]
