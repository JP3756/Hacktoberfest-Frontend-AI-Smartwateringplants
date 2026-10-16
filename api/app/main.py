from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import Base, engine, get_db
from app.models import PumpModeModel, SensorDataModel
from app.schemas import PumpModeRequest, SensorDataRequest

app = FastAPI()
active_websocket: WebSocket | None = None


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/sensor-data/")
async def get_sensor_data(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorDataModel))
    return result.scalars().all()


@app.post("/pump-mode/")
async def create_pump_mode(
    body: PumpModeRequest,
    db: AsyncSession = Depends(get_db),
):
    new_pump_mode = PumpModeModel(mode=body.pump_mode)
    db.add(new_pump_mode)
    await db.commit()
    await db.refresh(new_pump_mode)

    if active_websocket:
        await active_websocket.send_json({"pump_mode": new_pump_mode.mode})
    return new_pump_mode


@app.get("/pump-mode/")
async def get_pump_mode(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PumpModeModel))
    return result.scalars().all()


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
            new_sensor_data = SensorDataModel(
                moisture_level=sensor_data_validated.moisture_level,
                water_level=sensor_data_validated.water_level,
            )
            db.add(new_sensor_data)
            await db.commit()
            await db.refresh(new_sensor_data)
    except WebSocketDisconnect:
        pass
    active_websocket = None
