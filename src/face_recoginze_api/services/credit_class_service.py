from typing import List, Optional
from face_recoginze_api.repositories.credit_class_repository import CreditClassRepository
from face_recoginze_api.models.models import CreditClass
from sqlmodel.ext.asyncio.session import AsyncSession
from face_recoginze_api.DTOs.dtos import CreditClassRead

class CreditClassService:
    def __init__(self, session: AsyncSession):
        self.repo = CreditClassRepository(session=session)

    async def list_credit_classes(self) -> List[CreditClassRead]:
        classes = await self.repo.get_all()
        return [CreditClassRead.model_validate(cl) for cl in classes]


    async def get_credit_class(self, id: int) -> Optional[CreditClass]:
        return await self.repo.get_by_id(id)

    async def create_credit_class(self, name: str) -> CreditClass:
        credit_class = CreditClass(name=name)
        return await self.repo.create(credit_class)

    async def update_credit_class(self, id: int, name: str) -> Optional[CreditClass]:
        return await self.repo.update(id, {"name": name})

    async def delete_credit_class(self, id: int) -> bool:
        return await self.repo.delete(id)
