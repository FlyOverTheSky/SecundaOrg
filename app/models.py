from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("activities.id"))

    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent")
    organization_activities = relationship("OrganizationActivity", back_populates="activity")


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    organizations = relationship("Organization", back_populates="building")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)

    building = relationship("Building", back_populates="organizations")
    phones = relationship("OrganizationPhone", back_populates="organization", cascade="all, delete-orphan")
    organization_activities = relationship("OrganizationActivity", back_populates="organization", cascade="all, delete-orphan")


class OrganizationPhone(Base):
    __tablename__ = "organization_phones"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    phone = Column(String, nullable=False)

    organization = relationship("Organization", back_populates="phones")


class OrganizationActivity(Base):
    __tablename__ = "organization_activities"

    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), primary_key=True)

    organization = relationship("Organization", back_populates="organization_activities")
    activity = relationship("Activity", back_populates="organization_activities")
