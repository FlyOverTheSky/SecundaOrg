from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from sqlalchemy.sql import text
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_X, ST_Y, ST_GeogFromText

from app.models import Activity, Building, Organization, OrganizationPhone, OrganizationActivity
from app.schemas import BuildingCreate, OrganizationCreate, ActivityCreate


EARTH_RADIUS_METERS = 6371000  # Approximate Earth radius in meters


def get_activity_depth(db: Session, activity_id: int) -> int:
    query = text(
        """
        WITH RECURSIVE activity_path AS (
            SELECT id, parent_id, 1 AS depth
            FROM activities
            WHERE id = :activity_id
            UNION ALL
            SELECT a.id, a.parent_id, ap.depth + 1
            FROM activities a
            JOIN activity_path ap ON a.id = ap.parent_id
        )
        SELECT MAX(depth) FROM activity_path;
        """
    )
    result = db.execute(query, {"activity_id": activity_id}).scalar()
    return result or 0


def create_activity(db: Session, activity: ActivityCreate) -> Activity:
    if activity.parent_id:
        parent_depth = get_activity_depth(db, activity.parent_id)
        if parent_depth >= 3:
            raise ValueError("Activity nesting exceeds 3 levels")
    db_activity = Activity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def create_building(db: Session, building: BuildingCreate) -> Building:
    location = ST_GeogFromText(f"POINT({building.longitude} {building.latitude})")
    db_building = Building(address=building.address, location=location)
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building


def create_organization(db: Session, organization: OrganizationCreate) -> Organization:
    db_organization = Organization(name=organization.name, building_id=organization.building_id)
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    
    for phone in organization.phones:
        db_phone = OrganizationPhone(organization_id=db_organization.id, phone=phone)
        db.add(db_phone)
    
    for activity_id in organization.activity_ids:
        db_assoc = OrganizationActivity(organization_id=db_organization.id, activity_id=activity_id)
        db.add(db_assoc)
    
    db.commit()
    db.refresh(db_organization)
    return db_organization


def get_organization(db: Session, org_id: int) -> Optional[Organization]:
    return (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.organization_activities).joinedload(OrganizationActivity.activity)
        )
        .filter(Organization.id == org_id)
        .first()
    )


def get_organizations_by_name(db: Session, name: str) -> List[Organization]:
    return (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.organization_activities).joinedload(OrganizationActivity.activity)
        )
        .filter(Organization.name.ilike(f"%{name}%"))
        .all()
    )


def get_organizations_in_building(db: Session, building_id: int) -> List[Organization]:
    return (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.organization_activities).joinedload(OrganizationActivity.activity)
        )
        .filter(Organization.building_id == building_id)
        .all()
    )


def get_buildings(db: Session) -> List[Building]:
    return db.query(Building).all()


def get_organizations_by_activity(db: Session, activity_id: int) -> List[Organization]:
    return (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.organization_activities).joinedload(OrganizationActivity.activity)
        )
        .join(OrganizationActivity)
        .filter(OrganizationActivity.activity_id == activity_id)
        .all()
    )


def get_descendant_activities(db: Session, activity_id: int) -> List[int]:
    recursive_cte = (
        select(Activity.id.label("id"))
        .where(Activity.id == activity_id)
        .cte(name="descendants", recursive=True)
    )

    recursive_part = (
        select(Activity.id)
        .join(recursive_cte, Activity.parent_id == recursive_cte.c.id)
    )

    full_query = select(recursive_cte.union_all(recursive_part).c.id)
    result = db.execute(full_query).scalars().all()
    return list(result)


def get_organizations_by_activity_recursive(db: Session, activity_name: str) -> List[Organization]:
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        return []
    descendants = get_descendant_activities(db, activity.id)
    return (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.organization_activities).joinedload(OrganizationActivity.activity)
        )
        .join(OrganizationActivity)
        .filter(OrganizationActivity.activity_id.in_(descendants))
        .distinct()
        .all()
    )


def get_organizations_near(db: Session, lat: float, lon: float, radius: Optional[float] = None, width: Optional[float] = None, height: Optional[float] = None) -> List[Organization]:
    point = ST_MakePoint(lon, lat).ST_AsEWKT()
    if radius is not None:
        buildings = db.query(Building).filter(ST_DWithin(Building.location, point, radius)).all()
    elif width is not None and height is not None:
        # Approximate calculation for bounding box
        delta_lat = height / (2 * 111000)  # 1 degree lat ~ 111 km
        delta_lon = width / (2 * 111000 * func.cos(func.radians(lat)))
        lat_min = lat - delta_lat
        lat_max = lat + delta_lat
        lon_min = lon - delta_lon
        lon_max = lon + delta_lon
        buildings = db.query(Building).filter(
            ST_X(Building.location).between(lon_min, lon_max),
            ST_Y(Building.location).between(lat_min, lat_max)
        ).all()
    else:
        return []

    building_ids = [b.id for b in buildings]
    return (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.organization_activities).joinedload(OrganizationActivity.activity)
        )
        .filter(Organization.building_id.in_(building_ids))
        .all()
    )
