
from sqlalchemy.orm import Session
from core.database import Listing, User, Transaction
from models import ListingCreateRequest
import uuid

async def create_listing(db: Session, request: ListingCreateRequest):
    listing = Listing(
        seller_id=request.sellerId,
        type=request.type,
        category=request.category,
        title=request.title,
        description=request.description,
        price=request.price,
        unit=request.unit,
        images=request.images,
        status="active"
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing

async def search_listings(db: Session, query: str = None, type: str = None):
    q = db.query(Listing).filter(Listing.status == "active")
    if type:
        q = q.filter(Listing.type == type)
    if query:
        q = q.filter((Listing.title.ilike(f"%{query}%")) | (Listing.description.ilike(f"%{query}%")))

    return q.all()

async def initiate_transaction(db: Session, from_user_id: str, to_user_id: str, amount: float, type: str, reference_id: str):
    transaction = Transaction(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        amount=amount,
        type=type,
        status="pending",
        reference_id=reference_id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
