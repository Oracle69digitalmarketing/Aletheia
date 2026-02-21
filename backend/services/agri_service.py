
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from core.database import User, Farmer, Location
from core.agent_utils import get_llm_client
from models import FarmerRegisterRequest, AdviceResponse

async def register_farmer(db: Session, request: FarmerRegisterRequest):
    # Check if user exists
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        user = User(
            phone=request.phone,
            name=request.name,
            language=request.language,
            role="farmer"
        )
        db.add(user)
        db.flush()

    # Add/Update location
    location = db.query(Location).filter(Location.user_id == user.id, Location.is_primary == True).first()
    if not location:
        location = Location(user_id=user.id, lga=request.lga, is_primary=True)
        db.add(location)
    else:
        location.lga = request.lga

    # Add/Update Farmer record
    farmer = db.query(Farmer).filter(Farmer.user_id == user.id).first()
    if not farmer:
        farmer = Farmer(user_id=user.id, crops=request.crops, subscriptions=request.subscriptions)
        db.add(farmer)
    else:
        farmer.crops = request.crops
        farmer.subscriptions = request.subscriptions

    db.commit()
    db.refresh(user)
    return user

async def get_farmer_advice(db: Session, farmer_id: str):
    user = db.query(User).filter(User.id == farmer_id).first()
    if not user:
        return None

    farmer = db.query(Farmer).filter(Farmer.user_id == user.id).first()
    location = db.query(Location).filter(Location.user_id == user.id, Location.is_primary == True).first()

    crops_str = ", ".join([c.get('type', 'unknown') for c in farmer.crops]) if farmer and farmer.crops else "general crops"
    lga = location.lga if location else "Ondo State"

    prompt = f"""
    You are the Ondo Connect Agri-Advisor.
    Provide a concise, highly actionable agricultural advice for a farmer in {lga} growing {crops_str}.
    Include a mention of the current season in Nigeria.
    Language: {user.language}
    """

    advice_text = "Keep up the good work on your farm!"
    try:
        llm_info = get_llm_client()
        client = llm_info["client"]
        model = llm_info["model"]

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        advice_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Agri-Advice Error: {e}")

    return AdviceResponse(
        farmerId=farmer_id,
        advice=advice_text,
        weatherAlert="Moderate rainfall expected this week. Ensure proper drainage.",
        marketPrices={"Cocoa": "₦2,500/kg", "Cassava": "₦800/bag"}
    )
