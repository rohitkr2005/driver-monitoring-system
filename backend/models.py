from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_no = Column(String)
    dashcam_id = Column(String)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String)
    alert_type = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)