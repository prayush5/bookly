from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import UserCreateModel, UserLoginModel
from sqlmodel import select, desc
from .models import User
from .utils import verify_password, generate_passwd_hash
import uuid

class UserService:
    async def  get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email ==  email)

        result = await session.exec(statement)

        user = result.first()

        return user
    
    async def get_user_by_uid(self, uid: uuid.UUID, session: AsyncSession):
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        user = result.first()
        return user
    
    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return user is not None
    
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        password = user_data_dict.pop("password")
        new_user = User(
            **user_data_dict,
            password_hash=generate_passwd_hash(password)
        )
        new_user.role = "user"

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
