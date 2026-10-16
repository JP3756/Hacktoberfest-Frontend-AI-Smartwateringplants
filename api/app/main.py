from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import Base, engine, get_db
from app.models import Pump, PumpMode, SensorData
from app.schemas import PumpModeRequest, SensorDataRequest

app = FastAPI()
active_websocket: WebSocket | None = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7357", "http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/sensor/")
async def get_sensor(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorData))
    return result.scalars().all()


@app.get("/sensor-data/")
async def get_sensor_data(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorData))
    return result.scalars().all()


@app.get("/pump/")
async def get_pump(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Pump))
    return result.scalars().all()


@app.get("/pump-mode/")
async def get_pump_mode(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PumpMode))
    return result.scalars().all()


@app.put("/pump-mode/")
async def update_pump_mode(
    body: PumpModeRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PumpMode).where(PumpMode.pump_id == body.pump))
    db_pump_mode = result.scalars().first()

    if db_pump_mode:
        db_pump_mode.mode = body.pump_mode
    else:
        db_pump_mode = PumpMode(pump_id=body.pump, mode=body.pump_mode)
        db.add(db_pump_mode)

    await db.commit()
    await db.refresh(db_pump_mode)

    if active_websocket:
        await active_websocket.send_json(
            {"pump": db_pump_mode.pump_id, "pump_mode": db_pump_mode.mode}
        )
    return db_pump_mode


@app.websocket("/mc-ws/")
async def mc_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    global active_websocket
    await websocket.accept()
    active_websocket = websocket
    try:
        while True:
            sensor_data = await websocket.receive_json()
            sensor_data_validated = SensorDataRequest.model_validate_json(sensor_data)
            new_sensor_data = SensorData(
                sensor_id=sensor_data_validated.sensor,
                moisture_level=sensor_data_validated.moisture_level,
                water_level=sensor_data_validated.water_level,
            )
            db.add(new_sensor_data)
            await db.commit()
            await db.refresh(new_sensor_data)
    except WebSocketDisconnect:
        pass
    active_websocket = None
