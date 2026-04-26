import xml.etree.ElementTree as ET
from pathlib import Path

from connect_db import get_db
from models import MotorPart

XML_FILE = Path("inventory.xml")


def load_inventory_from_xml():
    """
    This function reads inventory.xml and saves motor parts into MySQL.
    It will only load the XML data if the motor_parts table is empty.
    This prevents stock from resetting every time you restart the app.
    """

    if not XML_FILE.exists():
        raise FileNotFoundError("inventory.xml was not found.")

    db = get_db()

    try:
        existing_parts = db.query(MotorPart).count()

        if existing_parts > 0:
            return

        tree = ET.parse(XML_FILE)
        root = tree.getroot()

        for item in root.findall("Part"):
            part = MotorPart(
                id=int(item.findtext("ID")),
                name=item.findtext("Name", ""),
                brand=item.findtext("Brand", ""),
                category=item.findtext("Category", ""),
                price=float(item.findtext("Price", "0")),
                stock=int(item.findtext("Stock", "0")),
                image_url=item.findtext("ImageURL", "")
            )

            db.add(part)

        db.commit()

    finally:
        db.close()


def get_all_parts(search_text=None):
    """
    This function gets all motor parts from MySQL.
    """

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
    """
    This function gets one motor part by ID.
    """

    db = get_db()

    try:
        return db.get(MotorPart, int(part_id))

    finally:
        db.close()


def update_stock(part_id, new_stock):
    """
    This function updates stock in MySQL.
    """

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