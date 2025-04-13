from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
from face_recoginze_api.models.models import CreditClass  # cập nhật path nếu cần

class CreditClassRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[CreditClass]:
        statement = select(CreditClass)
        result = await self.session.exec(statement)
        return result.all()

    async def get_by_id(self, id: int) -> Optional[CreditClass]:
        return await self.session.get(CreditClass, id)

    async def create(self, credit_class: CreditClass) -> CreditClass:
        self.session.add(credit_class)
        await self.session.commit()
        await self.session.refresh(credit_class)
        return credit_class

    async def update(self, id: int, new_data: dict) -> Optional[CreditClass]:
        db_class = await self.get_by_id(id)
        if not db_class:
            return None
        for key, value in new_data.items():
            setattr(db_class, key, value)
        self.session.add(db_class)
        await self.session.commit()
        await self.session.refresh(db_class)
        return db_class

    async def delete(self, id: int) -> bool:
        db_class = await self.get_by_id(id)
        if not db_class:
            return False
        await self.session.delete(db_class)
        await self.session.commit()
        return True
