from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://username:password@localhost/dbname"
# DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/dbname"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Sadece SQLite için gerekli
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Her istek için bir veritabanı oturumu sağlar.
    İşlem tamamlandığında oturumu kapatır.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
