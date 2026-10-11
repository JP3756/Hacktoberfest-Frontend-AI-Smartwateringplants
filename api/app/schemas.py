from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="User's full name")
    email: EmailStr = Field(description="Must be a valid email address")
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password must be at least 8 characters long",
    )


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=20, description="Valid JWT refresh token string"
    )
