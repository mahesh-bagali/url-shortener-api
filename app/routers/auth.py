
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.database.session import get_session
from app.models import User
from app.schemas.users import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserResponse,
)
from app.services.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.services.rate_limiter import limiter


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
def register_user(
    payload: UserRegisterRequest,
    session: Session = Depends(get_session),
) -> UserResponse:
    """Create a user account using a hashed password."""

    statement = select(User).where(User.email == str(payload.email))
    existing_user = session.exec(statement).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="Log in and receive an access token",
)
@limiter.limit("5/minute")
def login_user(
    request: Request,
    payload: UserLoginRequest,
    session: Session = Depends(get_session),
) -> UserLoginResponse:
    """Verify credentials and return a JWT access token."""

    statement = select(User).where(User.email == str(payload.email))
    user = session.exec(statement).first()

    if user is None or not verify_password(
        payload.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to identify user",
        )

    access_token = create_access_token(user.id)

    return UserLoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the profile of the authenticated user."""

    return UserResponse.model_validate(current_user)
