from sqlmodel.ext.asyncio.session import AsyncSession
from face_recoginze_api.DTOs.dtos import AttendanceRecordCreate, AttendanceRecordRead
from ..repositories.attendance_repository import AttendanceRepository
from typing import List

class AttendanceService:
    def __init__(self, repo: AttendanceRepository):
        self.repo = repo

    async def create_attendance(self, db: AsyncSession, data: AttendanceRecordCreate) -> AttendanceRecordRead:
        record = await self.repo.create(db, data)
        return AttendanceRecordRead.model_validate(record)

    async def get_all_attendance(self, db: AsyncSession) -> List[AttendanceRecordRead]:
        """
        Lấy tất cả bản ghi điểm danh và trả về dưới dạng danh sách AttendanceRecordRead.
        """
        records = await self.repo.get_all(db)
        return [AttendanceRecordRead.model_validate(record) for record in records]

    async def get_attendance_by_user_id(self, db: AsyncSession, user_id: int) -> List[AttendanceRecordRead]:
        """
        Lấy tất cả bản ghi điểm danh của một người dùng và trả về dưới dạng danh sách AttendanceRecordRead.
        """
        records = await self.repo.get_by_user_id(db, user_id)
        return [AttendanceRecordRead.model_validate(record) for record in records]

    async def get_attendance_by_class_id(self, db: AsyncSession, class_id: int) -> List[AttendanceRecordRead]:
        """
        Lấy tất cả bản ghi điểm danh của một lớp học và trả về dưới dạng danh sách AttendanceRecordRead.
        """
        records = await self.repo.get_by_class_id(db, class_id)
        return [AttendanceRecordRead.model_validate(record) for record in records]