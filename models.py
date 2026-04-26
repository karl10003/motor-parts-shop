from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from connect_db import Base


class MotorPart(Base):
    __tablename__ = "motor_parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    brand = Column(String(80), nullable=False)
    category = Column(String(80), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    image_url = Column(String(500), nullable=True)

    orders = relationship("Order", back_populates="part")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(60), unique=True, nullable=False)
    part_id = Column(Integer, ForeignKey("motor_parts.id"), nullable=False)
    customer_name = Column(String(120), nullable=False)
    quantity = Column(Integer, nullable=False)
    payment_method = Column(String(60), nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    part = relationship("MotorPart", back_populates="orders")