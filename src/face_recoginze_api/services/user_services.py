from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List
from face_recoginze_api.models.models import User
from face_recoginze_api.DTOs.dtos import UserDTO
from face_recoginze_api.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository()

    async def create_user(self, userDTO: UserDTO) -> Optional[int]:
        """Tạo user mới"""
        return await self.user_repository.add(user_dto=userDTO, db=self.session)
        
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Lấy user theo ID"""
        return await self.user_repository.get_by_id(user_id=user_id, db=self.session)

    # async def get_all_users(self) -> List[User]:
    #     """Lấy danh sách tất cả users"""
    #     statement = self.user_repository.statement_get_all_users()
    #     result = await self.session.exec(statement)
    #     return result.all()

    # async def update_user_name(self, user_id: int, new_name: str) -> bool:
    #     """Cập nhật tên user"""
    #     user = await self.get_user_by_id(user_id)
    #     if user:
    #         user.name = new_name
    #         self.session.add(user)
    #         await self.session.commit()
    #         await self.session.refresh(user)
    #         return True
    #     return False

    async def delete_user(self, user_id: int) -> bool:
        """Xóa user theo ID"""
        return await self.user_repository.statement_delete_by_id(user_id=user_id, session=self.session)
        
