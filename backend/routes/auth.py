from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Admin
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# Proper DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    # Check if username already exists
    existing = db.query(Admin).filter(Admin.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = pwd_context.hash(password)
    admin = Admin(username=username, password=hashed)
    db.add(admin)
    db.commit()
    return {"message": "Admin created"}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == username).first()

    if not admin or not pwd_context.verify(password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful"}