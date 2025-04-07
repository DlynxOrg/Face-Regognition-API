from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from face_recoginze_api.models.models import Embedding, User, ArcFaceEmbedding
from face_recoginze_api.DTOs.dtos import EmbeddingDTO
import numpy as np
from face_recoginze_api.enums.enums import ErrorType

class EmbeddingRepository:
    async def get_with_users(self, db: AsyncSession) -> list[EmbeddingDTO]:
        query = select(Embedding, User).join(User, Embedding.user_id == User.id)
        result = await db.execute(query)
        rows = result.all()
        return [
            EmbeddingDTO(
                embedding_id=emb.id,
                vector=emb.vector.tolist() if isinstance(emb.vector, np.ndarray) else list(emb.vector),
                user_id=user.id,
                user_name=user.name
            ) for emb, user in rows
        ]
    
    async def get_arcface_with_users(self, db: AsyncSession) -> list[EmbeddingDTO]:
        query = select(ArcFaceEmbedding, User).join(User, ArcFaceEmbedding.user_id == User.id)
        result = await db.execute(query)
        rows = result.all()
        return [
            EmbeddingDTO(
                embedding_id=emb.id,
                vector=emb.vector.tolist() if isinstance(emb.vector, np.ndarray) else list(emb.vector),
                user_id=user.id,
                user_name=user.name
            ) for emb, user in rows
        ]

    async def add(self, db: AsyncSession, vector: list[float], user_id: int, image_id: int) -> str:
        try:
            new_embedding = Embedding(vector=vector, user_id=user_id, image_id=image_id)
            db.add(new_embedding)
            await db.commit()
            await db.refresh(new_embedding)
            return "Embedding added successfully"
        except Exception as e:
            print(f"Error: {str(e)}")
            return ErrorType.INTERNAL_SERVER_ERROR.value
        
    async def add_arcface(self, db: AsyncSession, vector: list[float], user_id: int, image_id: int) -> str:
        try:
            new_embedding = ArcFaceEmbedding(vector=vector, user_id=user_id, image_id=image_id)
            db.add(new_embedding)
            await db.commit()
            await db.refresh(new_embedding)
            return "Embedding added successfully"
        except Exception as e:
            print(f"Error: {str(e)}")
            return ErrorType.INTERNAL_SERVER_ERROR.value

    async def get_id_by_user_and_image(self, db: AsyncSession, user_id: int, image_id: int) -> int | None:
        statement = select(Embedding.id).where(
            Embedding.user_id == user_id,
            Embedding.image_id == image_id
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
