from sqlmodel.ext.asyncio.session import AsyncSession
from face_recoginze_api.DTOs.dtos import AttendanceRecordCreate, AttendanceRecordRead
from ..repositories.attendance_repository import AttendanceRepository

class AttendanceService:
    def __init__(self, repo: AttendanceRepository):
        self.repo = repo

    async def create_attendance(self, db: AsyncSession, data: AttendanceRecordCreate) -> AttendanceRecordRead:
        record = await self.repo.create(db, data)
        return AttendanceRecordRead.model_validate(record)
