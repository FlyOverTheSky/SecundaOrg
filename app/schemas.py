from typing import List, Optional
from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    name: str


class ActivityCreate(ActivityBase):
    parent_id: Optional[int] = None


class Activity(ActivityBase):
    id: int
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


class ActivityNested(Activity):
    children: List["ActivityNested"] = []


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True


class PhoneBase(BaseModel):
    phone: str


class Phone(PhoneBase):
    id: int

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    building_id: int
    phones: List[str] = []
    activity_ids: List[int] = []


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    building: Building
    phones: List[Phone]
    activities: List[Activity]

    class Config:
        from_attributes = True
