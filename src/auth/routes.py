from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from .schemas import UserCreateModel, UserModel, ForgotPasswordModel, ResetPasswordModel
from .service import UserService
from src.db.main import get_session, AsyncSession
from .utils import create_token, verify_password, decode_token, generate_passwd_hash
from .schemas import UserLoginModel
from datetime import timedelta
from .dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_user
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists, InvalidCredentials, UserNotFound, InvalidToken
from src.middleware import limiter

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()

REFRESH_TOKEN_EXPIRY = 1

@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def create_user_account(
    request: Request,
    user_data: UserCreateModel, 
    session:AsyncSession = Depends(get_session)
    ):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExists()
    
    new_user = await user_service.create_user(user_data, session)
    return new_user

@auth_router.post("/login")
@limiter.limit("5/minute")
async def login_users(request: Request, login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):

    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_token(
                user_data= {
                    'email': user.email,
                    'user_uid': str(user.uid),
                    "role": user.role
                }
            )

            refresh_token = create_token(
                user_data= {
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
    
    raise InvalidCredentials()

@auth_router.post("/refresh")
async def create_new_access_token(token_details = Depends(refresh_token_bearer)):
    user = token_details['user']

    if user is None:
        raise UserNotFound()
    
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    access_token = create_token(
        user_data = {
            "email": user['email'],
            "user_uid": user['user_uid']
        }
    )

    refresh_token = create_token(
        user_data = {
            "email": user['email'],
            "user_uid": user['user_uid']
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@auth_router.get("/me")
async def get_current_user(user = Depends(get_current_user)):
    return user

@auth_router.post("/logout")
async def revoke_token(token_details: dict = Depends(access_token_bearer)):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content= {
            "message": "Logged out successfully"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post("/forgot-password")
@limiter.limit("2/hour")
async def forgot_password(request: Request, password_data: ForgotPasswordModel, session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_email(password_data.email, session)
    if user is None:
        raise UserNotFound()
    
    reset_token = create_token(
        user_data={
            "user_uid": str(user.uid),
            "email": user.email
        },
        expiry=timedelta(minutes=10),
        purpose="password_reset"
    )

    return {
        "message": "Password reset token generated",
        "reset_token": reset_token
    }
    
@auth_router.post("/reset-password")
@limiter.limit("2/hour")
async def reset_password(request: Request, password_data: ResetPasswordModel, session: AsyncSession = Depends(get_session)):
    payload = decode_token(password_data.token)
    if payload is None:
        raise InvalidToken()
    
    if payload["purpose"] != "password_reset":
        raise InvalidToken()
    
    user_uid = payload["user"]["user_uid"]
    user = await user_service.get_user_by_uid(user_uid, session)

    if user is None:
        raise UserNotFound()
    
    hashed_password = generate_passwd_hash(password_data.new_password)
    user.password_hash = hashed_password

    await session.commit()
    await session.refresh(user)

    return {
        "message": "Password reset successful",
    }
