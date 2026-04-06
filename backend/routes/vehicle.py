from fastapi import APIRouter
from backend.database import SessionLocal
from backend.models import Vehicle

router = APIRouter()

def get_db():
    return SessionLocal()

@router.post("/add_vehicle")
def add_vehicle(vehicle_no: str, dashcam_id: str):
    db = get_db()

    vehicle = Vehicle(vehicle_no=vehicle_no, dashcam_id=dashcam_id)
    db.add(vehicle)
    db.commit()

    return {"message": "Vehicle added"}

@router.get("/vehicles")
def get_vehicles():
    db = get_db()
    vehicles = db.query(Vehicle).all()

    return vehicles