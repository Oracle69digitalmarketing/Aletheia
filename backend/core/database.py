
import os
import datetime
import uuid
from sqlalchemy import create_engine, Column, String, Float, Integer, JSON, DateTime, Boolean, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Use DATABASE_URL if available, else fallback to sqlite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ondo_connect.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    language = Column(String(2), default="en")
    role = Column(String)  # 'farmer', 'artisan', 'buyer', 'collector'
    wallet_balance = Column(DECIMAL(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)

    locations = relationship("Location", back_populates="user")

class Location(Base):
    __tablename__ = "locations"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    lga = Column(String)
    coordinates = Column(JSON)  # {lat: float, lng: float}
    is_primary = Column(Boolean, default=False)

    user = relationship("User", back_populates="locations")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=generate_uuid)
    from_user_id = Column(String, ForeignKey("users.id"))
    to_user_id = Column(String, ForeignKey("users.id"))
    amount = Column(DECIMAL(10, 2))
    type = Column(String)  # 'sale', 'booking', 'collection'
    status = Column(String)
    reference_id = Column(String)  # Links to specific module record
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    crops = Column(JSON)  # List of crop objects
    subscriptions = Column(JSON)  # List of strings: 'weather', 'prices', 'pest-alerts'

class Listing(Base):
    __tablename__ = "listings"
    id = Column(String, primary_key=True, default=generate_uuid)
    seller_id = Column(String, ForeignKey("users.id"))
    type = Column(String)  # 'product', 'service', 'waste'
    category = Column(String)
    title = Column(String)
    description = Column(String)
    price = Column(DECIMAL(10, 2))
    unit = Column(String)  # 'kg', 'unit', 'hour'
    images = Column(JSON)  # List of image URLs
    status = Column(String)  # 'active', 'sold', 'expired'
    location = Column(JSON)  # GeoJSON or simple {lat, lng}

class Artisan(Base):
    __tablename__ = "artisans"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    business_name = Column(String)
    category = Column(String)  # 'mechanic', 'tailor', etc.
    services = Column(JSON)  # List of service objects
    qr_code = Column(String)

class WasteCollection(Base):
    __tablename__ = "waste_collections"
    id = Column(String, primary_key=True, default=generate_uuid)
    requester_info = Column(JSON)  # {name, phone, address}
    waste_type = Column(String)  # 'plastic', 'agricultural', 'e-waste'
    estimated_kg = Column(Float)
    status = Column(String)  # 'requested', 'assigned', 'collected', 'weighed', 'paid'
    assigned_collector_id = Column(String, ForeignKey("users.id"), nullable=True)
    points_awarded = Column(Integer, default=0)
    photo_evidence = Column(String)  # URL

# Keeping PlanRecord for backward compatibility if needed, or we can remove it.
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
