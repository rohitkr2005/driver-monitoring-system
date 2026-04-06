from fastapi import FastAPI
from backend.routes import auth, vehicle, alert
from database import engine
import models

# CREATE TABLES
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(vehicle.router)
app.include_router(alert.router)

@app.get("/")
def home():
    return {"message": "Driver Monitoring Backend Running"}