"""
Seed script to populate the database with test data.

Run: python -m src.seed
"""

import asyncio
import logging

from sqlalchemy import text

from src.domain.models import Activity, Building, Organization
from src.infrastructure.database import async_session_factory

logger = logging.getLogger(__name__)


BUILDINGS_DATA = [
    {
        "address": "г. Москва, Ходынский бульвар, 4",
        "latitude": 55.790272,
        "longitude": 37.530019,
    },
    {
        "address": "г. Москва, ул. Тверская, 15",
        "latitude": 55.762373,
        "longitude": 37.607898,
    },
    {
        "address": "г. Москва, Кутузовский проспект, 24",
        "latitude": 55.744531,
        "longitude": 37.545267,
    },
    {
        "address": "г. Санкт-Петербург, Невский проспект, 28",
        "latitude": 59.935800,
        "longitude": 30.325875,
    },
    {
        "address": "г. Санкт-Петербург, улица Коллонтай, 3Б",
        "latitude": 59.911519,
        "longitude": 30.446802,
    },
    {
        "address": "г. Новосибирск, ул. Красный проспект, 50",
        "latitude": 55.035323,
        "longitude": 82.919792,
    },
]

ACTIVITIES_DATA = [
    {"name": "Еда", "parent_name": None, "level": 1},
    {"name": "Автомобили", "parent_name": None, "level": 1},
    {"name": "IT Услуги", "parent_name": None, "level": 1},
    {"name": "Строительство", "parent_name": None, "level": 1},
    {"name": "Мясная продукция", "parent_name": "Еда", "level": 2},
    {"name": "Молочная продукция", "parent_name": "Еда", "level": 2},
    {"name": "Выпечка", "parent_name": "Еда", "level": 2},
    {"name": "Грузовые", "parent_name": "Автомобили", "level": 2},
    {"name": "Легковые", "parent_name": "Автомобили", "level": 2},
    {"name": "Запчасти", "parent_name": "Автомобили", "level": 2},
    {"name": "Разработка ПО", "parent_name": "IT Услуги", "level": 2},
    {"name": "Консалтинг", "parent_name": "IT Услуги", "level": 2},
    {"name": "Аксессуары", "parent_name": "Запчасти", "level": 3},
    {"name": "Двигатели", "parent_name": "Запчасти", "level": 3},
    {"name": "Веб-разработка", "parent_name": "Разработка ПО", "level": 3},
    {
        "name": "Мобильная разработка",
        "parent_name": "Разработка ПО",
        "level": 3,
    },
]

ORGANIZATIONS_DATA = [
    {
        "name": 'ООО "Рога и Копыта"',
        "phone_numbers": ["2-222-222", "3-333-333"],
        "building_index": 0,
        "activity_names": ["Мясная продукция", "Молочная продукция"],
    },
    {
        "name": 'ООО "МясоМаркет"',
        "phone_numbers": ["8-923-666-13-13"],
        "building_index": 0,
        "activity_names": ["Мясная продукция"],
    },
    {
        "name": 'АО "АвтоТрейд"',
        "phone_numbers": ["4-444-444", "5-555-555"],
        "building_index": 1,
        "activity_names": ["Легковые", "Запчасти"],
    },
    {
        "name": 'ИП "Булочка"',
        "phone_numbers": ["6-666-666"],
        "building_index": 1,
        "activity_names": ["Выпечка"],
    },
    {
        "name": 'ООО "ТехноСофт"',
        "phone_numbers": ["7-777-777", "8-888-888", "9-999-999"],
        "building_index": 2,
        "activity_names": ["Веб-разработка", "Консалтинг"],
    },
    {
        "name": 'ЗАО "ГрузАвто"',
        "phone_numbers": ["8-951-666-66-66"],
        "building_index": 3,
        "activity_names": ["Грузовые", "Аксессуары"],
    },
    {
        "name": 'ООО "МобайлДев"',
        "phone_numbers": ["8-921-222-22-22"],
        "building_index": 2,
        "activity_names": ["Мобильная разработка"],
    },
    {
        "name": 'ООО "СтройМастер"',
        "phone_numbers": ["1-112-112", "1-123-123"],
        "building_index": 4,
        "activity_names": ["Строительство"],
    },
    {
        "name": 'АО "Молоко и Сливки"',
        "phone_numbers": ["2-133-133"],
        "building_index": 5,
        "activity_names": ["Молочная продукция"],
    },
    {
        "name": 'ООО "Все для Авто"',
        "phone_numbers": ["4-142-142", "5-151-151"],
        "building_index": 3,
        "activity_names": ["Легковые", "Грузовые", "Аксессуары", "Двигатели"],
    },
]


async def seed_database() -> None:
    """Create buildings, activities, organizations in DB if data is missing"""
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM buildings"))
        count = result.scalar_one()
        if count > 0:
            logger.info("Database already seeded, skipping.")
            return

        buildings = []
        for data in BUILDINGS_DATA:
            building = Building(
                address=data["address"],
                location=Building.make_location(float(data["latitude"]), float(data["longitude"])),
            )
            session.add(building)
            buildings.append(building)
        await session.flush()

        activity_map: dict[str, Activity] = {}
        for data in ACTIVITIES_DATA:
            parent_id = None
            if data["parent_name"] is not None:
                parent_id = activity_map[str(data["parent_name"])].id

            activity = Activity(
                name=data["name"],
                parent_id=parent_id,
                level=data["level"],
            )
            session.add(activity)
            await session.flush()
            activity_map[str(data["name"])] = activity

        for data in ORGANIZATIONS_DATA:
            b_idx = data.get("building_index")
            if not isinstance(b_idx, int):
                continue
            org = Organization(
                name=data["name"],
                phone_numbers=data["phone_numbers"],
                building_id=buildings[b_idx].id,
            )
            activity_names = data.get("activity_names", [])
            if not isinstance(activity_names, list):
                activity_names = []
            for activity in activity_names:
                org.activities.append(activity_map[activity])
            session.add(org)

        await session.commit()
        logger.info("Database seeded successfully!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_database())
