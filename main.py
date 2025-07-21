# app/main.py
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from database import Base,engine
from routes.router import router
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Plastic Injection Production Tracking",
    description="An API that manages and monitors plastic injection molding processes, production cycles, molds, operators, and quality control metrics.",
    version="1.0.0",
    summary="API documentation for plastic injection manufacturing operations monitoring",
    contact={
        "name": "Override Yazılım",
        "url": "https://override.com.tr",
        "email": "info@override.com.tr",
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "defaultModelRendering": "example",
        "displayRequestDuration": True,
        "docExpansion": "none",
        "deepLinking": True,
        "filter": False,
        "operationsSorter": "alpha",
        "tryItOutEnabled": True,
        "persistAuthorization": True
    }
)

origins = [
    # "http://localhost",
    # "http://localhost:8080",
    # "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RequestLogger")
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Request Method: {request.method}")
    logger.info(f"Request Headers: {request.headers}")
    logger.info(f"Request Body: {body.decode('utf-8')}")
    response = await call_next(request)
    return response

# from database import SessionLocal
# db=SessionLocal()
# from models import User
# from auth import get_password_hash

# user=User(
#     username="admin",
#     password=get_password_hash("admin"),
#     user_type="admin",
#     factory_id=1
# )

# db.add(user)
# db.commit()