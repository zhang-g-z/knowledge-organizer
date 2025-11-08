from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from .. import crud, schemas
from ..database import get_db
from ..core import security
from ..schemas import PasswordChange
from ..core.security import get_current_user

router = APIRouter()


@router.post("/auth/register", response_model=schemas.UserRead)
async def register(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # check username/email/phone uniqueness
    if await crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user_in.email and await crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_in.phone and await crud.get_user_by_phone(db, user_in.phone):
        raise HTTPException(status_code=400, detail="Phone already registered")
    hashed = security.get_password_hash(user_in.password)
    user = await crud.create_user(db, username=user_in.username, hashed_password=hashed, name=user_in.name, phone=user_in.phone, email=user_in.email)
    return user


@router.post("/auth/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, form_data.username)
    print(form_data.password, user.hashed_password)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/change_password")
async def change_password(payload: PasswordChange, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    # validate confirm
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")
    user = await crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # verify old password
    if not security.verify_password(payload.old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Old password incorrect")
    # set new password
    new_hash = security.get_password_hash(payload.new_password)
    user.hashed_password = new_hash
    db.add(user)
    await db.commit()
    return {"ok": True}


@router.post("/auth/token_json", response_model=schemas.Token)
async def login_for_access_token_json(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Compatibility endpoint: accept JSON {username, password} for clients that cannot send form-encoded data."""
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")
    user = await crud.get_user_by_username(db, username)
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}
