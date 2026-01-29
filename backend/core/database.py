
from sqlalchemy import create_engine, Column, String, Float, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aletheia.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PlanRecord(Base):
    __tablename__ = "plans"

    id = Column(String, primary_key=True, index=True)
    user_email = Column(String, index=True)
    goal = Column(String)
    category = Column(String)
    tasks = Column(JSON)
    reasoning = Column(JSON)
    friction_intervention = Column(String)
    metrics = Column(JSON)
    trace_id = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
