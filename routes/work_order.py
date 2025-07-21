from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from datetime import datetime,timedelta

from database import get_db
from models import WorkOrder, Order, MachineMold, Customer, OrderProduct, Machine, Mold
from schemas import WorkOrderCreate, WorkOrderUpdate, WorkOrderOut
from auth import get_current_user

router = APIRouter(prefix="/work-orders", tags=["work_orders"])

@router.post("/check-conflicting-workorders/")
def check_conflicting_workorders(db: Session = Depends(get_db)):
    warnings = []
    workorders = db.query(WorkOrder).all()

    for w in workorders:
        machine_mold = db.query(MachineMold).filter(MachineMold.id == w.machine_mold_id).first()
        if not machine_mold:
            continue  # veya logla

        machine_id = machine_mold.machine_id
        mold_id = machine_mold.mold_id

        # Çakışan zaman aralığı için filtre
        overlapping_filter = (
            (WorkOrder.planned_start_datetime < w.planned_end_datetime) &
            (WorkOrder.planned_end_datetime > w.planned_start_datetime) &
            (WorkOrder.id != w.id)  # kendisiyle karşılaştırma olmasın
        )

        # Aynı kalıp farklı makinede çalışıyor mu?
        mold_conflicts = (
            db.query(WorkOrder)
            .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id)
            .filter(
                MachineMold.mold_id == mold_id,
                MachineMold.machine_id != machine_id,
                overlapping_filter
            )
            .all()
        )

        # Aynı makinede farklı kalıp çalışıyor mu?
        machine_conflicts = (
            db.query(WorkOrder)
            .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id)
            .filter(
                MachineMold.machine_id == machine_id,
                MachineMold.mold_id != mold_id,
                overlapping_filter
            )
            .all()
        )

        if mold_conflicts or machine_conflicts:
            warnings.append({
                "work_order_id": w.id,
                "machine_id": machine_id,
                "mold_id": mold_id,
                "planned_start": w.planned_start_datetime,
                "planned_end": w.planned_end_datetime,
                "mold_conflicts": [
                    {
                        "conflict_work_order_id": c.id,
                        "conflict_machine_id": db.query(MachineMold).get(c.machine_mold_id).machine_id,
                        "conflict_start": c.planned_start_datetime,
                        "conflict_end": c.planned_end_datetime
                    } for c in mold_conflicts
                ],
                "machine_conflicts": [
                    {
                        "conflict_work_order_id": c.id,
                        "conflict_mold_id": db.query(MachineMold).get(c.machine_mold_id).mold_id,
                        "conflict_start": c.planned_start_datetime,
                        "conflict_end": c.planned_end_datetime
                    } for c in machine_conflicts
                ]
            })
    return warnings



@router.post("/", response_model=WorkOrderOut, status_code=status.HTTP_201_CREATED)
def create_work_order(data: WorkOrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order_product = db.query(OrderProduct) \
        .join(Order, OrderProduct.order_id==Order.id) \
        .join(Customer,Order.customer_id==Customer.id) \
        .filter(
            Customer.factory_id == current_user.factory_id,
            OrderProduct.id == data.order_product_id) \
        .first()
    
    machine_mold = db.query(MachineMold) \
        .join(Machine,MachineMold.machine_id==Machine.id) \
        .join(Mold, MachineMold.mold_id==Mold.id) \
        .filter(
            Machine.factory_id == current_user.factory_id,
            Mold.factory_id==current_user.factory_id, 
            MachineMold.id == data.machine_mold_id) \
        .first()

    if not order_product or not machine_mold :
        raise HTTPException(status_code=400, detail="Order, Machine, or Mold not found.")

    overlapping_filter = (
                (WorkOrder.planned_start_datetime < data.planned_end_datetime) &
                (WorkOrder.planned_end_datetime > data.planned_start_datetime) 
            )

    # Aynı kalıp farklı makinede çalışıyor mu?
    mold_conflicts = (
        db.query(WorkOrder)
        .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id)
        .filter(
            MachineMold.mold_id == machine_mold.mold_id,
            MachineMold.machine_id != machine_mold.machine_id,
            overlapping_filter
        )
        .all()
    )

    # Aynı makinede farklı kalıp çalışıyor mu?
    machine_conflicts = (
        db.query(WorkOrder)
        .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id)
        .filter(
            MachineMold.machine_id == machine_mold.machine_id,
            MachineMold.mold_id != machine_mold.mold_id,
            overlapping_filter
        )
        .all()
    )

    if mold_conflicts or machine_conflicts:
        raise HTTPException(status_code=400, detail={
            "machine_mold_id": data.machine_mold_id,
            "planned_start": str(data.planned_start_datetime),
            "planned_end": str(data.planned_end_datetime),
            "mold_conflicts": [
                {
                    "conflict_work_order_id": c.id,
                    "conflict_machine_id": db.query(MachineMold).get(c.machine_mold_id).machine_id,
                    "conflict_start": str(c.planned_start_datetime),
                    "conflict_end": str(c.planned_end_datetime),
                    "order_product_id":c.order_product_id
                } for c in mold_conflicts
            ],
            "machine_conflicts": [
                {
                    "conflict_work_order_id": c.id,
                    "conflict_mold_id": db.query(MachineMold).get(c.machine_mold_id).mold_id,
                    "conflict_start": str(c.planned_start_datetime),
                    "conflict_end": str(c.planned_end_datetime),
                    "order_product_id":c.order_product_id
                } for c in machine_conflicts
            ]
        })

    record = WorkOrder(**data.dict())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred.")

    return record


@router.get("/", response_model=List[WorkOrderOut])
def list_work_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    start_date: datetime = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: datetime = Query(None, description="Filter by end date (YYYY-MM-DD)")
):
    query = db.query(WorkOrder) \
        .join(OrderProduct, WorkOrder.order_product_id == OrderProduct.id) \
        .join(Order, OrderProduct.order_id == Order.id) \
        .join(Customer, Order.customer_id == Customer.id) \
        .filter(Customer.factory_id == current_user.factory_id)
    
    query = query.filter(WorkOrder.planned_end_datetime >= start_date,WorkOrder.planned_start_datetime <= end_date+timedelta(days=1))
    
    return query.all()

@router.get("/machine-mold/{machine_mold_id}", response_model=List[WorkOrderOut])
def list_work_orders_by_related_machine_molds(machine_mold_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Önce verilen machine_mold kaydının makine ve kalıp ID'lerini bulalım
    target_machine_mold = db.query(MachineMold).filter(MachineMold.id == machine_mold_id).first()
    
    if not target_machine_mold:
        raise HTTPException(status_code=404, detail="Belirtilen Machine-Mold kaydı bulunamadı")
    
    # Aynı makineyi VEYA aynı kalıbı kullanan tüm machine_mold kayıtlarını bulalım
    related_machine_mold_ids = db.query(MachineMold.id).filter(
        or_(
            MachineMold.machine_id == target_machine_mold.machine_id,
            MachineMold.mold_id == target_machine_mold.mold_id
        )
    ).all()
    
    # Bu ID'leri liste formatına çevirelim
    related_ids = [mm_id for (mm_id,) in related_machine_mold_ids]
    
    # Bu machine_mold ID'lerine sahip tüm iş emirlerini getirelim
    return db.query(WorkOrder) \
        .join(OrderProduct, WorkOrder.order_product_id == OrderProduct.id) \
        .join(Order, OrderProduct.order_id == Order.id) \
        .join(Customer, Order.customer_id == Customer.id) \
        .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id) \
        .join(Machine, MachineMold.machine_id == Machine.id) \
        .join(Mold, MachineMold.mold_id == Mold.id) \
        .filter(
            Customer.factory_id == current_user.factory_id,
            WorkOrder.planned_end_datetime >= datetime.now(),
            WorkOrder.machine_mold_id.in_(related_ids)
        ) \
        .all()


@router.get("/order-product/{order_product_id}", response_model=List[WorkOrderOut])
def list_work_orders_by_order_product(order_product_id:int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(WorkOrder) \
        .join(OrderProduct, WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order, Order.customer_id==Customer.id) \
        .join(Customer, Order.customer_id==Customer.id) \
        .filter(
            Customer.factory_id == current_user.factory_id,
            WorkOrder.order_product_id== order_product_id
            ) \
        .all()

@router.get("/{work_order_id}", response_model=WorkOrderOut)
def get_work_order(work_order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(WorkOrder) \
        .join(OrderProduct, WorkOrder.order_product_id==OrderProduct.id) \
        .join(Order, Order.customer_id==Customer.id) \
        .join(Customer, Order.customer_id==Customer.id) \
        .filter(
            Customer.factory_id == current_user.factory_id,
            WorkOrder.id==work_order_id) \
        .first()
    if not record:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    return record


@router.put("/{work_order_id}", response_model=WorkOrderOut)
def update_work_order(work_order_id: int, data: WorkOrderUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(WorkOrder).join(OrderProduct, WorkOrder.order_product_id==OrderProduct.id).join(Order, Order.customer_id==Customer.id).join(Customer, Order.customer_id==Customer.id).filter(Customer.factory_id == current_user.factory_id, WorkOrder.id==work_order_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="WorkOrder not found")

    if data.order_product_id:
        order_product = db.query(OrderProduct).join(Order, OrderProduct.order_id==Order.id).join(Customer,Order.customer_id==Customer.id).filter(Customer.factory_id == current_user.factory_id, OrderProduct.id == data.order_product_id).first()
        if not order_product:
            raise HTTPException(status_code=400, detail="Order-Product not found.")
        
    if data.machine_mold_id:
        machine_mold = db.query(MachineMold).join(Machine,MachineMold.machine_id==Machine.id).join(Mold, MachineMold.mold_id==Mold.id).filter(Machine.factory_id == current_user.factory_id,Mold.factory_id==current_user.factory_id, MachineMold.id == data.machine_mold_id).first()
        if not machine_mold:
            raise HTTPException(status_code=400, detail="Machine-Mold not found.")


    overlapping_filter = (
                (WorkOrder.planned_start_datetime < data.planned_end_datetime) &
                (WorkOrder.planned_end_datetime > data.planned_start_datetime) &
                (WorkOrder.id != work_order_id)
            )

    # Aynı kalıp farklı makinede çalışıyor mu?
    mold_conflicts = (
        db.query(WorkOrder)
        .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id)
        .filter(
            MachineMold.mold_id == machine_mold.mold_id,
            MachineMold.machine_id != machine_mold.machine_id,
            overlapping_filter
        )
        .all()
    )

    # Aynı makinede farklı kalıp çalışıyor mu?
    machine_conflicts = (
        db.query(WorkOrder)
        .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id)
        .filter(
            MachineMold.machine_id == machine_mold.machine_id,
            MachineMold.mold_id != machine_mold.mold_id,
            overlapping_filter
        )
        .all()
    )

    if mold_conflicts or machine_conflicts:
        raise HTTPException(status_code=400, detail={
            "machine_mold_id": data.machine_mold_id,
            "planned_start": str(data.planned_start_datetime),
            "planned_end": str(data.planned_end_datetime),
            "mold_conflicts": [
                {
                    "conflict_work_order_id": c.id,
                    "conflict_machine_id": db.query(MachineMold).get(c.machine_mold_id).machine_id,
                    "conflict_start": str(c.planned_start_datetime),
                    "conflict_end": str(c.planned_end_datetime),
                    "order_product_id":c.order_product_id
                } for c in mold_conflicts
            ],
            "machine_conflicts": [
                {
                    "conflict_work_order_id": c.id,
                    "conflict_mold_id": db.query(MachineMold).get(c.machine_mold_id).mold_id,
                    "conflict_start": str(c.planned_start_datetime),
                    "conflict_end": str(c.planned_end_datetime),
                    "order_product_id":c.order_product_id
                } for c in machine_conflicts
            ]
        })


    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_order(work_order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    record = db.query(WorkOrder).join(OrderProduct, WorkOrder.order_product_id==OrderProduct.id).join(Order, Order.customer_id==Customer.id).join(Customer, Order.customer_id==Customer.id).filter(Customer.factory_id == current_user.factory_id, WorkOrder.id==work_order_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="WorkOrder not found")

    db.delete(record)
    db.commit()





@router.get("/machine/{machine_id}", response_model=List[WorkOrderOut])
def list_work_orders_by_related_machines(machine_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Önce verilen machine_mold kaydının makine ve kalıp ID'lerini bulalım
    target_machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not target_machine:
        raise HTTPException(status_code=404, detail="Belirtilen Machine kaydı bulunamadı")
    
    # Aynı makineyi VEYA aynı kalıbı kullanan tüm machine_mold kayıtlarını bulalım
    related_machine_mold_ids = db.query(MachineMold.id).filter(
        or_(
            MachineMold.machine_id == target_machine.id
        )
    ).all()
    
    # Bu ID'leri liste formatına çevirelim
    related_ids = [mm_id for (mm_id,) in related_machine_mold_ids]
    
    # Bu machine_mold ID'lerine sahip tüm iş emirlerini getirelim
    return db.query(WorkOrder) \
        .join(OrderProduct, WorkOrder.order_product_id == OrderProduct.id) \
        .join(Order, OrderProduct.order_id == Order.id) \
        .join(Customer, Order.customer_id == Customer.id) \
        .join(MachineMold, WorkOrder.machine_mold_id == MachineMold.id) \
        .join(Machine, MachineMold.machine_id == Machine.id) \
        .join(Mold, MachineMold.mold_id == Mold.id) \
        .filter(
            Customer.factory_id == current_user.factory_id,
            WorkOrder.planned_end_datetime >= datetime.now(),
            WorkOrder.machine_mold_id.in_(related_ids)
        ) \
        .all()
