from app.core.security import verify_password, create_access_token

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse, ForgotPasswordSchema, ResetPasswordSchema, ChangePasswordSchema
from app.core.security import hash_password, verify_password
from app.schemas.user import UserLogin, TokenResponse

from app.core.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordSchema,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Password reset request accepted",
        "note": "Use /auth/reset-password to set new password"
    }


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordSchema,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(body.new_password)
    db.commit()

    return {
        "message": "Password reset successful"
    }


@router.post("/change-password")
def change_password(
    body: ChangePasswordSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.old_password, current_user.password):
        raise HTTPException(
            status_code=400,
            detail="Old password is incorrect"
        )

    current_user.password = hash_password(body.new_password)
    db.commit()

    return {
        "message": "Password changed successfully"
    }
