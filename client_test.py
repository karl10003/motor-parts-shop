from connect_db import create_tables
from inventory_service import load_inventory_from_xml, get_all_parts

create_tables()
load_inventory_from_xml()

print("Motor Parts Loaded from XML to Database:")

for part in get_all_parts():
    print(
        f"{part.id}. {part.name} | {part.brand} | "
        f"₱{part.price} | Stock: {part.stock}"
    )