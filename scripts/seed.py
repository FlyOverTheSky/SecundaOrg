import sys
from pathlib import Path

# Фикс `no module named "app"`
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings
from app.crud import create_activity, create_building, create_organization
from app.schemas import ActivityCreate, BuildingCreate, OrganizationCreate

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

eda = create_activity(db, ActivityCreate(name="Еда"))
myasnaya = create_activity(db, ActivityCreate(name="Мясная продукция", parent_id=eda.id))
molocnaya = create_activity(db, ActivityCreate(name="Молочная продукция", parent_id=eda.id))
avto = create_activity(db, ActivityCreate(name="Автомобили"))
gruz = create_activity(db, ActivityCreate(name="Грузовые", parent_id=avto.id))
legk = create_activity(db, ActivityCreate(name="Легковые", parent_id=avto.id))
zapchasti = create_activity(db, ActivityCreate(name="Запчасти", parent_id=legk.id))

b1 = create_building(db, BuildingCreate(address="г. Москва, ул. Ленина 1, офис 3", latitude=55.7558, longitude=37.6173))
b2 = create_building(db, BuildingCreate(address="г. Москва, ул. Блюхера 32/1", latitude=55.7935, longitude=37.7015))

org1 = create_organization(
    db,
    OrganizationCreate(
        name="ООО Рога и Копыта",
        building_id=b1.id,
        phones=["2-222-222", "3-333-333", "8-923-666-13-13"],
        activity_ids=[myasnaya.id, molocnaya.id],
    )
)
org2 = create_organization(
    db,
    OrganizationCreate(
        name="АвтоСервис",
        building_id=b2.id,
        phones=["4-444-444"],
        activity_ids=[zapchasti.id],
    )
)
org3 = create_organization(
    db,
    OrganizationCreate(
        name="МолокоФерма",
        building_id=b1.id,
        phones=["5-555-555"],
        activity_ids=[molocnaya.id],
    )
)

db.close()

print("Test data seeded successfully.")
