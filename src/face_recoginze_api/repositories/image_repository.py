from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from face_recoginze_api.models.models import Image  # Import model Image
from pathlib import Path
from fastapi import UploadFile
from face_recoginze_api.DTOs.dtos import ImageMetadata
from sqlmodel import update

class ImageRepository:
    async def save_metadata(self, db: AsyncSession, file: UploadFile, file_path: str) -> ImageMetadata:
        file_size = file.file.seek(0, 2)
        file.file.seek(0)

        image = Image(
            filename=file.filename,
            content_type=file.content_type,
            file_size=file_size,
            storage_path=str(Path(file_path).as_posix())
        )

        db.add(image)
        await db.commit()
        await db.refresh(image)
        return ImageMetadata(image_id=image.id)

    async def get_by_id(self, db: AsyncSession, image_id: int) -> Image | None:
        result = await db.execute(select(Image).where(Image.id == image_id))
        row = result.first()
        return row[0] if row else None

    async def delete_by_id(self, db: AsyncSession, image_id: int) -> bool:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        if image:
            await db.delete(image)
            await db.commit()
            return True
        return False

    async def update_is_validate_by_id(self, db: AsyncSession, image_id: int) -> bool:
        statement = (
            update(Image)
            .where(Image.id == image_id)
            .values(is_validate=True)
        )
        result = await db.execute(statement)
        await db.commit()
        return result.rowcount > 0
