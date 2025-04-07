import cv2 as cv
import numpy as np
from fastapi import UploadFile, HTTPException
import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
from face_recoginze_api.DTOs.dtos import ImageMetadata
from face_recoginze_api.enums.enums import ReadFileError, ErrorType
import asyncio
from pathlib import Path
from face_recoginze_api.repositories.image_repository import ImageRepository

class ImageService:
    SAVE_DIR = "src/images"

    def __init__(self):
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        self.image_repository = ImageRepository()

    def read_image(self, file: UploadFile):
        
        file_bytes = np.frombuffer(file.file.read(), np.uint8)
        frame = cv.imdecode(file_bytes, cv.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=500, detail="An error occur while trying to read image.")

        return frame
    
    async def save_image(self, file: UploadFile, db: AsyncSession) -> ImageMetadata:
        ext = os.path.splitext(file.filename)[1]  # Lấy phần mở rộng file (.jpg, .png, ...)
        new_filename = f"{uuid.uuid4().hex}{ext}"  # Tạo tên mới bằng UUID
        file_path = os.path.join(self.SAVE_DIR, new_filename)

        try:
            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(await file.read())  # Đọc và ghi file async
                return await self.image_repository.save_metadata(db, file, file_path)  # Lưu thông tin file vào database
                # Trả về đường dẫn file đã lưu
        except Exception as e:
            print(f"An error occur while trying to save file: {e}")
            raise e
        return None
    
    async def read_img_by_id(self, image_id, db: AsyncSession):
        metatada = await self.image_repository.get_by_id(db=db, image_id=image_id)
        try:
            if metatada:
                storage_path = Path(metatada.storage_path).as_posix()
                storage_path = storage_path.replace("\\", "/")
                async with aiofiles.open(storage_path, "rb") as file:  # Mở file ở chế độ nhị phân
                    content = await file.read()
                return None, content  # Trả về dữ liệu nhị phân của ảnh
            return ReadFileError.METADATA_NOT_FOUND.value, None
        except FileNotFoundError as e:
            print(f"An error occurred while trying to read the file: {e}")
            return ReadFileError.FILE_NOT_FOUND.value, None
        except Exception as e:
            print(f"An error occurred while trying to delete the file: {e}")
            return ErrorType.INTERNAL_SERVER_ERROR.value  # Lỗi không xác định
        
    async def delete_img_by_id(self, image_id, db: AsyncSession):
        metadata = await self.image_repository.get_by_id(db=db, image_id=image_id)
        try:
            if metadata:
                storage_path = metadata.storage_path
                if not metadata.is_validate:
                    await asyncio.to_thread(os.remove, storage_path)  # Xóa file async-friendly
                    await self.image_repository.delete_by_id(session=db, image_id=image_id)
                return None  # Xóa thành công
            return ReadFileError.METADATA_NOT_FOUND.value  # Không tìm thấy file
        except FileNotFoundError:
            return ReadFileError.FILE_NOT_FOUND.value  # File không tồn tại
        except Exception as e:
            print(f"An error occurred while trying to delete the file: {e}")
            return ErrorType.INTERNAL_SERVER_ERROR.value  # Lỗi không xác định