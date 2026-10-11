from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.database import Base, engine, get_db
from app.deps import get_current_user
from app.models import RefreshTokenModel, UserModel, SensorDataModel
from app.schemas import RefreshTokenRequest, UserLoginRequest, UserRegisterRequest
from app.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/sensor-data/")
async def get_sensor_data(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorDataModel))
    return result.scalars().all()


@app.post("/sensor-data/")
async def create_sensor_data(name: str, email: str, db: AsyncSession = Depends(get_db)):
    new_sensor_data = SensorDataModel(name=name, email=email)
    db.add(new_sensor_data)
    await db.commit()
    await db.refresh(new_sensor_data)
    return new_sensor_data


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.email == body.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(body.password)
    new_user = UserModel(
        name=body.name, email=body.email, hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    return {"message": "User registered successfully"}


@app.post("/login")
async def login(body: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.email == body.email))
    user = result.scalars().first()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    access_token = create_access_token(
        data={"sub": user.email}, token_version=user.token_version
    )
    refresh_token_str = create_refresh_token(
        data={"sub": user.email}, token_version=user.token_version
    )

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    db_refresh_token = RefreshTokenModel(
        token=refresh_token_str, user_id=user.id, expires_at=expires_at
    )
    db.add(db_refresh_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }


@app.post("/refresh")
async def refresh_access_token(
    body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    try:
        payload = jwt.decode(
            body.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise credentials_exception
        email: str = payload.get("sub")
        token_version: int = payload.get("ver")
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.execute(
        select(RefreshTokenModel).where(RefreshTokenModel.token == body.refresh_token)
    )
    db_token = result.scalars().first()
    if not db_token:
        raise credentials_exception

    user_result = await db.execute(select(UserModel).where(UserModel.email == email))
    user = user_result.scalars().first()

    if not user or not user.is_active or user.token_version != token_version:
        raise credentials_exception

    new_access_token = create_access_token(
        data={"sub": user.email}, token_version=user.token_version
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@app.post("/logout")
async def logout(
    body: RefreshTokenRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RefreshTokenModel).where(
            RefreshTokenModel.token == body.refresh_token,
            RefreshTokenModel.user_id == current_user.id,
        )
    )
    db_token = result.scalars().first()
    if db_token:
        await db.delete(db_token)
        await db.commit()

    return {"message": "Successfully logged out"}


@app.get("/users/me")
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }
