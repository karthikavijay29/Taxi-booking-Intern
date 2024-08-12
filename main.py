from fastapi import FastAPI
import uvicorn
from models import State
from routes import router

app = FastAPI(
    title="Taxi Booking System",
    version="0.0.1",
    contact={"name": "Karthika", "email": "karthikavijay2004@gmail.com"},
)

@app.on_event("startup")
async def startup_event():
    app.state=State()
    app.state.reset()

app.include_router(router, prefix="/api")

setattr(app, "state", State())

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)