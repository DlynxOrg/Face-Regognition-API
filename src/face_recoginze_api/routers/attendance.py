from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from face_recoginze_api.DTOs.dtos import AttendanceRecordCreate, AttendanceRecordRead
from face_recoginze_api.services.attendance_service import AttendanceService
from face_recoginze_api.repositories.attendance_repository import AttendanceRepository
from face_recoginze_api.database.database import Database
from typing import List
from fastapi.responses import FileResponse

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


@router.get("/", response_model=List[AttendanceRecordRead])
async def get_all_attendance(
    db: AsyncSession = Depends(database.get_session)
):
    async with db as session:
        return await attendance_service.get_all_attendance(db=session)


@router.get("/user/{user_id}", response_model=List[AttendanceRecordRead])
async def get_attendance_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(database.get_session)
):
    async with db as session:
        return await attendance_service.get_attendance_by_user_id(db=session, user_id=user_id)


@router.get("/class/{class_id}", response_model=List[AttendanceRecordRead])
async def get_attendance_by_class_id(
    class_id: int,
    db: AsyncSession = Depends(database.get_session)
):
    async with db as session:
        return await attendance_service.get_attendance_by_class_id(db=session, class_id=class_id)
    
@router.post("/attendance/export", response_class=FileResponse)
async def export_attendance_excel(records: List[AttendanceRecordRead]):
    file_path = await attendance_service.export_to_excel(records)
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )