import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import faiss
import cv2 as cv
from mtcnn import MTCNN
from keras_facenet import FaceNet
from sqlmodel.ext.asyncio.session import AsyncSession
from face_recoginze_api.services.image_service import ImageService
from face_recoginze_api.DTOs.dtos import UserDTO, ValidateDTO
from face_recoginze_api.enums.enums import ErrorType, ReadFileError
from face_recoginze_api.repositories.user_repository import UserRepository
from face_recoginze_api.repositories.embedding_repository import EmbeddingRepository
from face_recoginze_api.repositories.image_repository import ImageRepository
import insightface

class ArcFaceRecognizeService:
    def __init__(self):

        self.image_service = ImageService()
        self.detector = MTCNN()
        self.facenet = FaceNet()
        self.index = None
        self.index_arcface = None
        self.index_to_name = {}
        self.arcface = insightface.app.FaceAnalysis()
        self.arcface.prepare(ctx_id=-1)
        self.user_repository = UserRepository()
        self.embedding_repository = EmbeddingRepository()
        self.image_repository = ImageRepository()

    async def init_faiss_index(self, db_session: AsyncSession):
        embeddings = await self.embedding_repository.get_arcface_with_users(db_session)
        if len(embeddings) > 0:
            self.labels = np.array([e.user_id for e in embeddings])  
            self.vectors = np.array([np.array(e.vector, dtype=np.float32) for e in embeddings])

            # Khởi tạo FAISS Index
            dimension = self.vectors.shape[1]
            self.index = faiss.IndexHNSWFlat(dimension, 32)
            self.index.add(self.vectors)

            # Ánh xạ chỉ số FAISS -> tên người
            self.index_to_name = {i: name for i, name in enumerate(self.labels)}
        
    async def recognize_face_faiss_arcface(self, db: AsyncSession, image_id, top_k=5, threshold=1.0) -> tuple[str, UserDTO]:
        """
        Tìm người gần nhất với face_vector bằng FAISS.
        Nếu khoảng cách > threshold, trả về 'Unknown'.
        """
        error, face_vector = await self.generate_face_embedding_from_image_arcface(db=db, image_id=image_id)

        if error:
            return error, None

        face_vector = np.array(face_vector).astype('float32').reshape(1, -1)
        D, I = self.index_arcface.search(face_vector, top_k)
        
        best_index = I[0][0]
        best_distance = D[0][0]
        
        if best_distance > threshold:
            return ErrorType.FACE_NOT_FOUND.value, None
        
        predicted_user_id = int(self.index_to_name[best_index])
        user = await self.user_repository.get_by_id(db = db, user_id=predicted_user_id)
        return None, UserDTO(id = user.id, username=user.name)
    

    async def generate_face_embedding_from_image_arcface(self, image_id: int, db: AsyncSession):
        error, img_content = await self.image_service.read_img_by_id(image_id=image_id, db=db)
        if error:
            return error, None

        try:
            # Chuyển đổi bytes thành numpy array trước khi decode
            np_img = np.frombuffer(img_content, np.uint8)
            frame = cv.imdecode(np_img, cv.IMREAD_COLOR)

            if frame is None:
                print("Error: Image decoding failed.")
                return ErrorType.INTERNAL_SERVER_ERROR.value, None  # 🔥 Trả về None nếu ảnh không hợp lệ

            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = self.detector.detect_faces(frame_rgb)
        except Exception as e:
            print(f"Error processing image: {e}")
            return ErrorType.INTERNAL_SERVER_ERROR.value
            
        if results:
            print(results)
            x, y, w, h = results[0]['box']
            face_img = frame[y: y+h, x: x+w]
            # face_img = cv.resize(face_img, (160, 160))
            # face_img = np.expand_dims(face_img, axis=0)
            # embedding = self.facenet.embeddings(face_img)
            embedding = self.arcface.get(face_img)
            return None, embedding
        return ErrorType.NO_FACE_DETECED.value, None

    async def validate_face(self, image_id: int, db_session: AsyncSession) -> str:
        error, embedding = await self.generate_face_embedding_from_image_arcface(image_id=image_id, db=db_session)
        if error: 
            return error
        return None
    
    async def validate_metadata(self, image_id: int, db_session: AsyncSession):
        face_error = await self.validate_face(image_id=image_id, db_session=db_session)
        if face_error:
            await self.image_service.delete_img_by_id(image_id=image_id, db=db_session)
            return face_error
        await self.image_repository.update_is_validate_by_id(image_id=image_id, db=db_session)
        return None
            
    async def validate_user_data(self, user_id: int, image_id: int, db_session: AsyncSession) -> str:
        error, userDTO = await self.recognize_face_faiss_arcface(db=db_session, image_id=image_id)
        if not error and userDTO.id != user_id:
            return ErrorType.USER_FACE_NOT_MATCH.value
        return None
    
    async def add_new_embedding(self, data: ValidateDTO, db: AsyncSession):
        user_data_error = await self.validate_user_data(user_id=data.user_id, image_id=data.image.image_id, db_session=db)
        if user_data_error:
            return user_data_error
        
        metadata = await self.image_repository.get_by_id(db=db, image_id=data.image.image_id)
        if not metadata:
            return ReadFileError.METADATA_NOT_FOUND.value
        if metadata.is_validate:
            is_embedding_exist = await self.embedding_repository.get_id_by_user_and_image(db=db, user_id=data.user_id, image_id=metadata.id)
            if is_embedding_exist:
                return ErrorType.IMAGE_HAS_BEEN_USED.value
            error, embedding = await self.generate_face_embedding_from_image_arcface(image_id=data.image.image_id, db=db)
            if error:
                return error
            embedding = embedding.flatten().tolist()  
            await self.add_to_faiss_index(user_id=data.user_id, vector=embedding)  
            return await self.embedding_repository.add_arcface(db=db, vector=embedding, image_id=data.image.image_id, user_id=data.user_id)

        return ErrorType.IMAGE_NOT_VALIDATE.value

    
    async def add_to_faiss_index(self, user_id: int, vector: list[float]):
        if not hasattr(self, "index") or self.index is None:
            print("FAISS Index chưa được khởi tạo!")
            return ErrorType.INTERNAL_SERVER_ERROR.value
        
        # Convert list[float] → numpy array
        new_vector = np.array(vector, dtype=np.float32).reshape(1, -1)  # Định dạng (1, 512)
        # Thêm vào FAISS
        self.index.add(new_vector)
        # Thêm user_id vào labels
        self.labels = np.append(self.labels, user_id)
        # Cập nhật ánh xạ FAISS -> user_id
        self.index_to_name[len(self.labels) - 1] = user_id  