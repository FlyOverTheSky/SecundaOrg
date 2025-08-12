from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.schemas import Building
from app.crud import get_buildings, get_organizations_in_building
from app.schemas import Organization
from app.dependencies import get_api_key, get_db_session
from sqlalchemy.orm import Session

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/", response_model=List[Building])
def list_buildings(db: Session = Depends(get_db_session), api_key: str = Depends(get_api_key)):
    buildings = get_buildings(db)
    return [
        Building(
            id=b.id,
            address=b.address,
            latitude=b.location.y,
            longitude=b.location.x,
        )
        for b in buildings
    ]


@router.get("/{building_id}/organizations", response_model=List[Organization])
def list_organizations_in_building(building_id: int, db: Session = Depends(get_db_session), api_key: str = Depends(get_api_key)):
    orgs = get_organizations_in_building(db, building_id)
    if not orgs:
        raise HTTPException(status_code=404, detail="No organizations found")
    return orgs
