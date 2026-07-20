from fastapi.security import HTTPBearer
from .utils import decode_token
from fastapi import status, Request, Depends
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from typing import List
from .models import User
from src.errors import InvalidToken, RefreshTokenRequired, AccessTokenRequired, InsufficientPermission

user_service = UserService()

class TokenValidator(HTTPBearer):
    async def __call__(self, request: Request):
        credentials =  await super().__call__(request)

        token = credentials.credentials

        payload = decode_token(token)

        if payload is None:
            raise InvalidToken()
        
        self.verify_token_data(payload)
        
        if await token_in_blocklist(payload['jti']):
            raise InvalidToken()

        return payload
    
    def verify_token_data(self, payload):
        pass
    

class RefreshTokenBearer(TokenValidator):
    def verify_token_data(self, payload):
        if not payload["refresh"]:
            raise RefreshTokenRequired()
        
class AccessTokenBearer(TokenValidator):
    def verify_token_data(self, payload):
        if payload["refresh"]:
            raise AccessTokenRequired()
        
async def get_current_user(token_details: dict  = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_uid = token_details['user']['user_uid']

    user = await user_service.get_user_by_uid(user_uid, session)

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()