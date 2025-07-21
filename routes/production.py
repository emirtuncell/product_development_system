from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from database import get_db
from models import Production, WorkOrder, OrderProduct, Order, Customer, Machine, Operator, MachineOperator
from schemas import ProductionCreate, ProductionUpdate, ProductionOut
from auth import get_current_user, get_current_user_ws

router = APIRouter(prefix="/productions", tags=["productions"])

@router.websocket("/ws")
async def websocket_productions(
    websocket: WebSocket,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    await websocket.accept()
    try:
        if token is None:
            await websocket.close(code=1008)
            return
        
        current_user = get_current_user_ws(token, db)
        if not current_user:
            await websocket.close(code=1008)
            return

        await websocket.send_text(f"Merhaba, {current_user.username}!")

        count=0
        while True:
            await websocket.send_text(f"{count} ad.")
            count+=1
            await asyncio.sleep(1)
            # data = await websocket.receive_text()
            # await websocket.send_text(f"Alındı: {data}")
    
    except WebSocketDisconnect:
        print("WebSocket bağlantısı koptu.")


@router.post("/", response_model=ProductionOut, status_code=status.HTTP_201_CREATED)
def create_production(data: ProductionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    work_order=db.query(WorkOrder) \
        .join(OrderProduct, WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order, Order.customer_id==Customer.id) \
        .join(Customer, Order.customer_id==Customer.id) \
        .filter(
            Customer.factory_id == current_user.factory_id,
            WorkOrder.id==data.work_order_id) \
        .first()
    if not work_order:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    
    machine_operator=db.query(MachineOperator) \
        .join(Machine,MachineOperator.machine_id==Machine.id) \
        .join(Operator, MachineOperator.operator_id==Operator.id) \
        .filter(
            Machine.factory_id == current_user.factory_id,
            Operator.factory_id==current_user.factory_id, 
            MachineOperator.id == data.machine_operator_id) \
        .first()
    if not machine_operator:
        raise HTTPException(status_code=404, detail="Machine-Operator not found")


    record = Production(**data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/", response_model=List[ProductionOut])
def list_productions(db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(Production) \
        .join(MachineOperator, Production.machine_operator_id==MachineOperator.id) \
        .join(Machine, MachineOperator.machine_id==Machine.id) \
        .join(Operator, MachineOperator.operator_id==Operator.id) \
        .join(WorkOrder,Production.work_order_id==WorkOrder.id) \
        .join(OrderProduct,WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order,OrderProduct.order_id==Order.id) \
        .join(Customer,Order.customer_id==Customer.id) \
        .filter(Customer.factory_id==current_user.factory_id) \
        .filter(Machine.factory_id==current_user.factory_id) \
        .filter(Operator.factory_id==current_user.factory_id) \
        .all()


@router.get("/work-order/{work_order_id}", response_model=List[ProductionOut])
def list_productions_by_work_order(work_order_id:int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(Production) \
        .join(MachineOperator, Production.machine_operator_id==MachineOperator.id) \
        .join(Machine, MachineOperator.machine_id==Machine.id) \
        .join(Operator, MachineOperator.operator_id==Operator.id) \
        .join(WorkOrder,Production.work_order_id==WorkOrder.id) \
        .join(OrderProduct,WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order,OrderProduct.order_id==Order.id) \
        .join(Customer,Order.customer_id==Customer.id) \
        .filter(Customer.factory_id==current_user.factory_id) \
        .filter(Machine.factory_id==current_user.factory_id) \
        .filter(Operator.factory_id==current_user.factory_id) \
        .filter(WorkOrder.id==work_order_id) \
        .all()


@router.get("/machine/{machine_id}", response_model=List[ProductionOut])
def list_productions_by_machine(machine_id:int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(Production) \
        .join(MachineOperator, Production.machine_operator_id==MachineOperator.id) \
        .join(Machine, MachineOperator.machine_id==Machine.id) \
        .join(Operator, MachineOperator.operator_id==Operator.id) \
        .join(WorkOrder,Production.work_order_id==WorkOrder.id) \
        .join(OrderProduct,WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order,OrderProduct.order_id==Order.id) \
        .join(Customer,Order.customer_id==Customer.id) \
        .filter(Customer.factory_id==current_user.factory_id) \
        .filter(Machine.factory_id==current_user.factory_id) \
        .filter(Operator.factory_id==current_user.factory_id) \
        .filter(Machine.id==machine_id) \
        .filter(Production.end_datetime==None) \
        .all()

@router.get("/{production_id}", response_model=ProductionOut)
def get_production(production_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    record = db.query(Production) \
        .join(MachineOperator, Production.machine_operator_id==MachineOperator.id) \
        .join(Machine, MachineOperator.machine_id==Machine.id) \
        .join(Operator, MachineOperator.operator_id==Operator.id) \
        .join(WorkOrder,Production.work_order_id==WorkOrder.id) \
        .join(OrderProduct,WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order,OrderProduct.order_id==Order.id) \
        .join(Customer,Order.customer_id==Customer.id) \
        .filter(Customer.factory_id==current_user.factory_id) \
        .filter(Machine.factory_id==current_user.factory_id) \
        .filter(Operator.factory_id==current_user.factory_id) \
        .filter(Production.id == production_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Production not found")
    return record

@router.put("/{production_id}", response_model=ProductionOut)
def update_production(production_id: int, data: ProductionUpdate, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    record = db.query(Production) \
        .join(MachineOperator, Production.machine_operator_id==MachineOperator.id) \
        .join(Machine, MachineOperator.machine_id==Machine.id) \
        .join(Operator, MachineOperator.operator_id==Operator.id) \
        .join(WorkOrder,Production.work_order_id==WorkOrder.id) \
        .join(OrderProduct,WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order,OrderProduct.order_id==Order.id) \
        .join(Customer,Order.customer_id==Customer.id) \
        .filter(Customer.factory_id==current_user.factory_id) \
        .filter(Machine.factory_id==current_user.factory_id) \
        .filter(Operator.factory_id==current_user.factory_id) \
        .filter(Production.id == production_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Production not found")
    if data.work_order_id:
        work_order=db.query(WorkOrder).join(OrderProduct, WorkOrder.order_product_id==OrderProduct.id).join(Order, Order.customer_id==Customer.id).join(Customer, Order.customer_id==Customer.id).filter(Customer.factory_id == current_user.factory_id,WorkOrder.id==data.work_order_id).first()
        if not work_order:
            raise HTTPException(status_code=404, detail="WorkOrder not found")
    if data.machine_operator_id:
        machine_operator=db.query(MachineOperator).join(Machine,MachineOperator.machine_id==Machine.id).join(Operator, MachineOperator.operator_id==Operator.id).filter(Machine.factory_id == current_user.factory_id,Operator.factory_id==current_user.factory_id, MachineOperator.id == data.machine_operator_id).first()
        if not machine_operator:
            raise HTTPException(status_code=404, detail="Machine-Operator not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

@router.delete("/{production_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_production(production_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    record = db.query(Production) \
        .join(MachineOperator, Production.machine_operator_id==MachineOperator.id) \
        .join(Machine, MachineOperator.machine_id==Machine.id) \
        .join(Operator, MachineOperator.operator_id==Operator.id) \
        .join(WorkOrder,Production.work_order_id==WorkOrder.id) \
        .join(OrderProduct,WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order,OrderProduct.order_id==Order.id) \
        .join(Customer,Order.customer_id==Customer.id) \
        .filter(Customer.factory_id==current_user.factory_id) \
        .filter(Machine.factory_id==current_user.factory_id) \
        .filter(Operator.factory_id==current_user.factory_id) \
        .filter(Production.id == production_id) \
        .first()
    if not record:
        raise HTTPException(status_code=404, detail="Production not found")
    db.delete(record)
    db.commit()
