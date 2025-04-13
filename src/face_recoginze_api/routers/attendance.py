from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from face_recoginze_api.DTOs.dtos import AttendanceRecordCreate, AttendanceRecordRead
from face_recoginze_api.services.attendance_service import AttendanceService
from face_recoginze_api.repositories.attendance_repository import AttendanceRepository
from face_recoginze_api.database.database import Database

router = APIRouter()
database = Database()
attendance_service = AttendanceService(repo=AttendanceRepository())

@router.post("/", response_model=AttendanceRecordRead)
async def create_attendance(
    data: AttendanceRecordCreate,
    db: AsyncSession = Depends(database.get_session)
):
    async with db as session:
        return await attendance_service.create_attendance(db=session, data=data)
