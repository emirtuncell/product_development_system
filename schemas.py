from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models import UserType

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    username: str
    user_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "password": "admin"
                }
            ]
        }
    }

class UserCreate(BaseModel):
    username:str
    password:str
    factory_id:int

class FactoryUserCreate(BaseModel):
    username:str
    password:str
    user_type:UserType


class FactoryUserUpdate(BaseModel):
    username:Optional[str] = None
    password:Optional[str] = None
    user_type:Optional[UserType] = None

class UserUpdate(BaseModel):
    username:Optional[str]
    password:Optional[str]
    factory_id:Optional[int]

class FactoryBase(BaseModel):
    name: str

class FactoryCreate(FactoryBase):
    pass

class FactoryUpdate(BaseModel):
    name: Optional[str] = None

class FactoryOut(FactoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class MachineBase(BaseModel):
    name: str

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None

class MachineOut(MachineBase):
    id: int
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)

class OperatorBase(BaseModel):
    firstname: str
    lastname: str

class OperatorCreate(OperatorBase):
    pass

class OperatorUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    is_deleted: Optional[bool] = None

class OperatorOut(OperatorBase):
    id: int
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class MoldBase(BaseModel):
    name: str

class MoldCreate(MoldBase):
    pass

class MoldUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None

class MoldOut(MoldBase):
    id: int
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)



class ProductBase(BaseModel):
    name: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None

class ProductOut(ProductBase):
    id: int
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    name: str

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None

class CustomerOut(CustomerBase):
    id: int
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class ScrapCauseBase(BaseModel):
    name: str

class ScrapCauseCreate(ScrapCauseBase):
    pass

class ScrapCauseUpdate(BaseModel):
    name: Optional[str] = None

class ScrapCauseOut(ScrapCauseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StopCauseBase(BaseModel):
    name: str
    is_planned: bool

class StopCauseCreate(BaseModel):
    name: str
    is_planned: Optional[bool] = False

class StopCauseUpdate(BaseModel):
    name: Optional[str] = None
    is_planned: Optional[bool]

class StopCauseOut(StopCauseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    customer_id: int
    order_datetime: datetime
    deadline_datetime: datetime

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    order_datetime: Optional[datetime] = None
    deadline_datetime: Optional[datetime] = None

class OrderOut(OrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class MachineMoldBase(BaseModel):
    machine_id: int
    mold_id: int
    setup_time: int
    cycle_time: int

class MachineMoldCreate(MachineMoldBase):
    pass

class MachineMoldUpdate(BaseModel):
    machine_id: Optional[int] = None
    mold_id: Optional[int] = None
    setup_time: Optional[int] = None
    cycle_time: Optional[int] = None

class MachineMoldOut(MachineMoldBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class MachineOperatorBase(BaseModel):
    machine_id: int
    operator_id: int

class MachineOperatorCreate(MachineOperatorBase):
    pass

class MachineOperatorUpdate(BaseModel):
    machine_id: Optional[int] = None
    operator_id: Optional[int] = None

class MachineOperatorOut(MachineOperatorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class MoldProductBase(BaseModel):
    mold_id: int
    product_id: int
    count: int

class MoldProductCreate(MoldProductBase):
    pass

class MoldProductUpdate(BaseModel):
    mold_id: Optional[int] = None
    product_id: Optional[int] = None
    count: Optional[int] = None

class MoldProductOut(MoldProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderProductBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int

class OrderProductCreate(OrderProductBase):
    pass

class OrderProductUpdate(BaseModel):
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None

class OrderProductOut(OrderProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)



class WorkOrderBase(BaseModel):
    order_product_id: int
    machine_mold_id: int
    quantity: int
    planned_start_datetime: datetime
    planned_end_datetime: Optional[datetime] = None

class WorkOrderCreate(WorkOrderBase):
    pass

class WorkOrderUpdate(BaseModel):
    order_product_id: Optional[int] = None
    machine_mold_id: Optional[int] = None
    quantity: Optional[int]
    planned_start_datetime: Optional[datetime] = None
    planned_end_datetime: Optional[datetime] = None

class WorkOrderOut(WorkOrderBase):
    id: int
    

    model_config = ConfigDict(from_attributes=True)

class ProductionBase(BaseModel):
    work_order_id: int
    machine_operator_id: int
    cavity_count: int
    start_datetime: datetime
    end_datetime: Optional[datetime] = None

class ProductionCreate(ProductionBase):
    pass

class ProductionUpdate(BaseModel):
    work_order_id: Optional[int] = None
    machine_operator_id: Optional[int] = None
    cavity_count: Optional[int] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

class ProductionOut(ProductionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class StopBase(BaseModel):
    machine_id: int
    stop_cause_id: Optional[int]
    start_datetime: datetime
    end_datetime: Optional[datetime] = None

class StopCreate(StopBase):
    pass

class StopUpdate(BaseModel):
    machine_id: Optional[int] = None
    stop_cause_id: Optional[int] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

class StopOut(StopBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ScrapBase(BaseModel):
    production_id: int
    scrap_cause_id: int
    quantity: int

class ScrapCreate(ScrapBase):
    pass

class ScrapUpdate(BaseModel):
    production_id: Optional[int] = None
    scrap_cause_id: Optional[int] = None
    quantity: Optional[int] = None

class ScrapOut(ScrapBase):
    id: int

    model_config = ConfigDict(from_attributes=True)