from fastapi import APIRouter, Depends, HTTPException
from routes import auth,factory,customer,machine,mold,machine_mold,product,mold_product,operator,machine_operator,order,stop_cause,scrap_cause, work_order,production,order_product,scrap,stop,factory_admin,factory_user


router=APIRouter()

router.include_router(auth.router)
router.include_router(customer.router)
router.include_router(factory.router)
router.include_router(machine_mold.router)
router.include_router(machine.router)
router.include_router(machine_operator.router)
router.include_router(mold.router)
router.include_router(mold_product.router)
router.include_router(operator.router)
router.include_router(order.router)
router.include_router(order_product.router)
router.include_router(product.router)
router.include_router(production.router)
router.include_router(scrap_cause.router)
router.include_router(scrap.router)
router.include_router(stop_cause.router)
router.include_router(stop.router)
router.include_router(work_order.router)
router.include_router(factory_admin.router)
router.include_router(factory_user.router)