from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from face_recoginze_api.models.models import AttendanceRecord
from face_recoginze_api.DTOs.dtos import AttendanceRecordCreate
from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm import selectinload


class AttendanceRepository:
    async def create(self, db: AsyncSession, data: AttendanceRecordCreate) -> AttendanceRecord:
        # Múi giờ Việt Nam (UTC +7)
        vietnam_tz = timezone(timedelta(hours=7))
        
        # Lấy thời gian hiện tại theo múi giờ Việt Nam
        timestamp_vn = datetime.now(vietnam_tz)

        # Tạo bản ghi mới với timestamp theo múi giờ Việt Nam
        new_record = AttendanceRecord(user_id=data.user_id, class_id=data.class_id, timestamp=timestamp_vn)
        print(f"time_stamp VN = {timestamp_vn}")
        
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)
        return new_record
    
    async def get_all(self, db: AsyncSession):
        stmt = select(AttendanceRecord).options(
            selectinload(AttendanceRecord.user),
            selectinload(AttendanceRecord.credit_class)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(self, db: AsyncSession, user_id: int):
        stmt = select(AttendanceRecord).where(AttendanceRecord.user_id == user_id).options(
            selectinload(AttendanceRecord.user),
            selectinload(AttendanceRecord.credit_class)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_class_id(self, db: AsyncSession, class_id: int):
        stmt = select(AttendanceRecord).where(AttendanceRecord.class_id == class_id).options(
            selectinload(AttendanceRecord.user),
            selectinload(AttendanceRecord.credit_class)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
