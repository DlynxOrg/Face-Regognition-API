from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from face_recoginze_api.models.models import User
from face_recoginze_api.DTOs.dtos import UserDTO
from sqlmodel import delete

class UserRepository:
    async def get_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_dto(self, db: AsyncSession, dto: UserDTO) -> int | None:
        result = await db.execute(select(User.id).where(User.name == dto.username))
        return result.scalar_one_or_none()

    async def add(self, db: AsyncSession, user_dto: UserDTO) -> int:
        try:
            new_user = User(name=user_dto.username)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user.id
        except Exception as e:
            await db.rollback()
            print(f"Error: {str(e)}")
            raise e

    def statement_get_by_id(self, user_id: int):
        return select(User).where(User.id == user_id)

    def statement_get_all(self):
        return select(User)

    async def statement_delete_by_id(self, user_id: int, session: AsyncSession):
        statement = delete(User).where(User.id == user_id)
        result = await session.execute(statement)
        await session.commit()
        return result.rowcount > 0
