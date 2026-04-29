import xml.etree.ElementTree as ET
from pathlib import Path

from connect_db import get_db
from models import MotorPart

XML_FILE = Path("inventory.xml")


def load_inventory_from_xml():
    """
    Reads inventory.xml and saves or updates motor parts in the database.
    It updates the image path from XML.
    It does not reset stock if the product already exists.
    """

    if not XML_FILE.exists():
        raise FileNotFoundError("inventory.xml was not found.")

    db = get_db()

    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()

        for item in root.findall("Part"):
            part_id = int(item.findtext("ID"))
            xml_stock = int(item.findtext("Stock", "0"))

            part = db.get(MotorPart, part_id)

            if part is None:
                part = MotorPart(
                    id=part_id,
                    stock=xml_stock
                )
                db.add(part)

            part.name = item.findtext("Name", "")
            part.brand = item.findtext("Brand", "")
            part.category = item.findtext("Category", "")
            part.price = float(item.findtext("Price", "0"))
            part.image_url = item.findtext("ImageURL", "")

        db.commit()

    finally:
        db.close()


def get_all_parts(search_text=None):
    db = get_db()

    try:
        query = db.query(MotorPart)

        if search_text:
            search_value = f"%{search_text}%"

            query = query.filter(
                (MotorPart.name.like(search_value)) |
                (MotorPart.brand.like(search_value)) |
                (MotorPart.category.like(search_value))
            )

        return query.order_by(MotorPart.id).all()

    finally:
        db.close()


def get_part_by_id(part_id):
    db = get_db()

    try:
        return db.get(MotorPart, int(part_id))

    finally:
        db.close()


def update_stock(part_id, new_stock):
    db = get_db()

    try:
        part = db.get(MotorPart, int(part_id))

        if not part:
            return False

        part.stock = int(new_stock)
        db.commit()

        return True

    finally:
        db.close()