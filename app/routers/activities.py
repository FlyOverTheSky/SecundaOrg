from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas import Organization
from app.crud import get_organizations_by_activity, get_organizations_by_activity_recursive
from app.dependencies import get_api_key, get_db_session
from sqlalchemy.orm import Session

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/{activity_id}/organizations", response_model=List[Organization])
def list_organizations_by_activity(activity_id: int, db: Session = Depends(get_db_session), api_key: str = Depends(get_api_key)):
    orgs = get_organizations_by_activity(db, activity_id)
    return orgs


@router.get("/search", response_model=List[Organization])
def search_organizations_by_activity(
    activity: str = Query(...,
                          description="Activity name to search, including sub-activities"),
    db: Session = Depends(get_db_session),
    api_key: str = Depends(get_api_key)
    ):

    orgs = get_organizations_by_activity_recursive(db, activity)
    if not orgs:
        raise HTTPException(status_code=404, detail="No organizations found for this activity")
    return orgs