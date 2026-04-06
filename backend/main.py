from fastapi import FastAPI
from backend.routes import auth, vehicle, alert
from backend.database import engine
import backend.models

# CREATE TABLES
backend.models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(vehicle.router)
app.include_router(alert.router)

@app.get("/")
def home():
    return {"message": "Driver Monitoring Backend Running"}