from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.models import MembershipStatus


class MembershipTypeBase(BaseModel):
    name: str
    duration_days: int
    price: float
    description: Optional[str] = None
    features: List[str] = []


class MembershipTypeCreate(MembershipTypeBase):
    pass


class MembershipTypeResponse(MembershipTypeBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MembershipCustomOptions(BaseModel):
    personal_training: bool = False
    group_classes: bool = True
    pool_access: bool = False
    spa_access: bool = False
    freezing_allowed: bool = False


class MembershipBase(BaseModel):
    membership_type_id: int
    custom_options: MembershipCustomOptions


class MembershipCreate(MembershipBase):
    pass


class MembershipResponse(BaseModel):
    id: int
    user_id: int
    membership_type: MembershipTypeResponse
    start_date: datetime
    end_date: datetime
    status: MembershipStatus
    custom_options: Dict[str, Any]
    pause_history: List[Dict[str, Any]]
    current_pause: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class MembershipPauseRequest(BaseModel):
    pause_days: int
    reason: str = "По запросу клиента"


class MembershipHistoryResponse(BaseModel):
    membership: MembershipResponse
    purchase_date: datetime
    total_price: float
    status_changes: List[Dict[str, Any]]

    class Config:
        from_attributes = True