from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint,
    Enum, Text, Float
)
from sqlalchemy.orm import relationship
from database import Base
import enum


class FactoryBase(Base):

    __abstract__ = True

    __table_args__ = (
        UniqueConstraint('name', 'factory_id', name='uix_name_factory_id'),
    )

# Enums
class UserType(enum.Enum):
    admin = "admin"
    factory_admin = "factory_admin"
    operator = "operator"
    planner = "planner"


class Factory(Base):
    __tablename__ = 'factories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    
    users = relationship("User", backref="factory", cascade="all, delete")
    machines = relationship("Machine", backref="factory", cascade="all, delete")
    molds = relationship("Mold", backref="factory", cascade="all, delete")
    products = relationship("Product", backref="factory", cascade="all, delete")
    operators = relationship("Operator", backref="factory", cascade="all, delete")
    customers = relationship("Customer", backref="factory", cascade="all, delete")
    stop_causes = relationship("StopCause", backref="factory", cascade="all, delete")
    scrap_causes = relationship("ScrapCause", backref="factory", cascade="all, delete")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='CASCADE'), nullable=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)

class Machine(FactoryBase):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='RESTRICT'), nullable=False)
    name = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False)



class Mold(FactoryBase):
    __tablename__ = 'molds'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='RESTRICT'), nullable=False)
    name = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False)

class Product(FactoryBase):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='RESTRICT'), nullable=False)
    name = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False)

class Operator(Base):
    __tablename__ = 'operators'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='RESTRICT'), nullable=False)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    is_deleted = Column(Boolean, default=False)



class Customer(FactoryBase):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='RESTRICT'), nullable=False)
    name = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False)

class StopCause(FactoryBase):
    __tablename__ = 'stop_causes'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    is_planned = Column(Boolean)

class ScrapCause(FactoryBase):
    __tablename__ = 'scrap_causes'
    id = Column(Integer, primary_key=True)
    factory_id = Column(Integer, ForeignKey('factories.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)

class MachineMold(Base):
    __tablename__ = 'machine_molds'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='RESTRICT'), nullable=False)
    mold_id = Column(Integer, ForeignKey('molds.id', ondelete='RESTRICT'), nullable=False)
    setup_time = Column(Integer)
    cycle_time = Column(Integer)
    UniqueConstraint('machine_id', 'mold_id', name='uq_machine_mold')

class MoldProduct(Base):
    __tablename__ = 'mold_products'
    id = Column(Integer, primary_key=True)
    mold_id = Column(Integer, ForeignKey('molds.id', ondelete='RESTRICT'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    count = Column(Integer)
    UniqueConstraint('mold_id', 'product_id', name='uq_mold_product')

class MachineOperator(Base):
    __tablename__ = 'machine_operators'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='RESTRICT'), nullable=False)
    operator_id = Column(Integer, ForeignKey('operators.id', ondelete='RESTRICT'), nullable=False)
    UniqueConstraint('machine_id', 'operator_id', name='uq_machine_operator')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False)
    order_datetime = Column(DateTime, nullable=False)
    deadline_datetime = Column(DateTime, nullable=False)

class OrderProduct(Base):
    __tablename__ = 'order_products'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)
    UniqueConstraint('order_id', 'product_id', name='uq_order_product')

class WorkOrder(Base):
    __tablename__ = 'work_orders'
    id = Column(Integer, primary_key=True)
    order_product_id = Column(Integer, ForeignKey('order_products.id', ondelete='RESTRICT'), nullable=False)
    machine_mold_id = Column(Integer, ForeignKey('machine_molds.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)
    planned_start_datetime = Column(DateTime, nullable=False)
    planned_end_datetime = Column(DateTime, nullable=False)

class Stop(Base):
    __tablename__ = 'stops'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='RESTRICT'), nullable=False)
    stop_cause_id = Column(Integer, ForeignKey('stop_causes.id', ondelete='RESTRICT'), nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)

class Production(Base):
    __tablename__ = 'productions'
    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, ForeignKey('work_orders.id', ondelete='RESTRICT'), nullable=False)
    machine_operator_id = Column(Integer, ForeignKey('machine_operators.id', ondelete='RESTRICT'), nullable=False)
    cavity_count = Column(Integer, nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)

class Scrap(Base):
    __tablename__ = 'scraps'
    id = Column(Integer, primary_key=True)
    production_id = Column(Integer, ForeignKey('productions.id', ondelete='CASCADE'), nullable=False)
    scrap_cause_id = Column(Integer, ForeignKey('scrap_causes.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)