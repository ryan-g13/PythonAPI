from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DB_URL = f'postgresql://postgres:{settings.database_password}@{settings.database_hostname}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## Old Version of connection logic for raw sql 
# while True:
#     try:
#         conn = psycopg2.connect(database="fastapi", user="postgres", password="*******", host="localhost", cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("DB Connection Succcess")
#         break
#     except Exception as error:
#         print("DB Connection failed: ", error)
#         time.sleep(3)
