from fastapi import APIRouter
from database import SessionLocal
from models import Alert

router = APIRouter()

def get_db():
    return SessionLocal()

@router.post("/alert")
def receive_alert(vehicle_id: str, alert_type: str):
    db = get_db()

    alert = Alert(vehicle_id=vehicle_id, alert_type=alert_type)
    db.add(alert)
    db.commit()

    return {"message": "Alert received"}

@router.get("/alerts")
def get_alerts():
    db = get_db()
    alerts = db.query(Alert).all()

    return alerts