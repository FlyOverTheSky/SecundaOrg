from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas import Organization
from app.crud import (
    get_organization,
    get_organizations_by_name,
    get_organizations_near,
)
from app.dependencies import get_api_key, get_db_session
from sqlalchemy.orm import Session

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/{org_id}", response_model=Organization)
def get_organization_by_id(org_id: int, db: Session = Depends(get_db_session), api_key: str = Depends(get_api_key)):
    org = get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/search_name", response_model=List[Organization])
def search_organizations_by_name(name: str, db: Session = Depends(get_db_session), api_key: str = Depends(get_api_key)):
    orgs = get_organizations_by_name(db, name)
    return orgs


@router.get("/near", response_model=List[Organization])
def get_organizations_near_point(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: Optional[float] = Query(None, description="Radius in meters"),
    width: Optional[float] = Query(None, description="Width of rectangular area in meters"),
    height: Optional[float] = Query(None, description="Height of rectangular area in meters"),
    db: Session = Depends(get_db_session),
    api_key: str = Depends(get_api_key)
):
    if radius is None and (width is None or height is None):
        raise HTTPException(status_code=400, detail="Provide either radius or both width and height")
    if radius is not None and (width is not None or height is not None):
        raise HTTPException(status_code=400, detail="Provide either radius or rectangular dimensions, not both")
    orgs = get_organizations_near(db, lat, lon, radius, width, height)
    return orgs