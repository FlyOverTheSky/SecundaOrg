from fastapi import FastAPI

from app.routers import organizations, buildings, activities
from app.database import Base, engine

app = FastAPI(
    title="Organizations Directory API",
    description="REST API for managing organizations, buildings, and activities.",
    version="1.0.0",
)

app.include_router(organizations.router)
app.include_router(buildings.router)
app.include_router(activities.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
