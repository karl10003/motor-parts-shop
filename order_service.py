from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from sqlalchemy.orm import joinedload

from connect_db import get_db
from models import MotorPart, Order

ORDERS_XML = Path("orders.xml")


def create_orders_xml_if_missing():
    """
    This function creates orders.xml if it does not exist.
    """

    if ORDERS_XML.exists():
        return

    root = ET.Element("Orders")
    tree = ET.ElementTree(root)
    tree.write(ORDERS_XML, encoding="utf-8", xml_declaration=True)


def save_order_to_xml(order, part):
    """
    This function saves the order record into orders.xml.
    """

    create_orders_xml_if_missing()

    tree = ET.parse(ORDERS_XML)
    root = tree.getroot()

    order_node = ET.SubElement(root, "Order")

    ET.SubElement(order_node, "OrderCode").text = order.order_code
    ET.SubElement(order_node, "CustomerName").text = order.customer_name
    ET.SubElement(order_node, "PartName").text = part.name
    ET.SubElement(order_node, "Quantity").text = str(order.quantity)
    ET.SubElement(order_node, "PaymentMethod").text = order.payment_method
    ET.SubElement(order_node, "TotalAmount").text = str(order.total_amount)
    ET.SubElement(order_node, "Date").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tree.write(ORDERS_XML, encoding="utf-8", xml_declaration=True)


def create_order(part_id, customer_name, quantity, payment_method):
    """
    This function creates an order.
    It also reduces the stock after successful purchase.
    """

    db = get_db()

    try:
        part = db.get(MotorPart, int(part_id))

        if not part:
            return False, "Motor part not found."

        quantity = int(quantity)

        if quantity <= 0:
            return False, "Quantity must be greater than zero."

        if part.stock < quantity:
            return False, f"Not enough stock. Available stock: {part.stock}"

        total = part.price * quantity
        order_code = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S%f")

        order = Order(
            order_code=order_code,
            part_id=part.id,
            customer_name=customer_name,
            quantity=quantity,
            payment_method=payment_method,
            total_amount=total
        )

        part.stock = part.stock - quantity

        db.add(order)
        db.commit()

        db.refresh(order)
        db.refresh(part)

        save_order_to_xml(order, part)

        return True, f"Order successful! Order Code: {order.order_code}"

    except Exception as error:
        db.rollback()
        return False, str(error)

    finally:
        db.close()


def get_orders():
    """
    This function gets all recent orders from the database.
    """

    db = get_db()

    try:
        orders = (
            db.query(Order)
            .options(joinedload(Order.part))
            .order_by(Order.id.desc())
            .all()
        )

        return orders

    finally:
        db.close()