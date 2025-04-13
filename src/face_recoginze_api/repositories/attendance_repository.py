from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from face_recoginze_api.models.models import AttendanceRecord
from face_recoginze_api.DTOs.dtos import AttendanceRecordCreate
from datetime import datetime, timezone, timedelta

class AttendanceRepository:
    async def create(self, db: AsyncSession, data: AttendanceRecordCreate) -> AttendanceRecord:
        # Múi giờ Việt Nam (UTC +7)
        vietnam_tz = timezone(timedelta(hours=7))
        
        # Lấy thời gian hiện tại theo múi giờ Việt Nam
        timestamp_vn = datetime.now(vietnam_tz)

        # Chuyển thời gian về UTC trước khi lưu vào cơ sở dữ liệu
        timestamp_utc = timestamp_vn.astimezone(timezone.utc)

        # Tạo bản ghi mới với timestamp UTC
        new_record = AttendanceRecord(user_id=data.user_id, class_id=data.class_id, timestamp=timestamp_utc)
        
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)
        return new_record
