from pydantic import BaseModel
from typing import Optional
from enum import Enum
from typing import List
from datetime import datetime, timedelta

class ResponseMessage(BaseModel):
    status: str
    message: str
    code: Optional[int] = None
    data: Optional[object] = None

class ResponseSuccesss(BaseModel):
    detail: ResponseMessage

class EmbeddingDTO(BaseModel):
    embedding_id: int
    vector: List[float]
    user_id: int
    user_name: str

class UserDTO(BaseModel):
    id: Optional[int] = None
    name: str
    class Config:
        from_attributes = True

class ImageMetadata(BaseModel):
    image_id: int

class ValidateDTO(BaseModel):
    image: ImageMetadata
    user_id: int

class AttendanceDTO(BaseModel):
    id: int
    username: str
    class_name: str
    timestamp: datetime

class CreditClassCreate(BaseModel):
    name: str

class CreditClassRead(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class AttendanceRecordCreate(BaseModel):
    user_id: int
    class_id: int

class AttendanceRecordRead(BaseModel):
    id: int
    timestamp: datetime
    user: UserDTO
    credit_class: CreditClassRead

    model_config = {"from_attributes": True}

    @property
    def timestamp(self) -> datetime:
        return self.__dict__["timestamp"] + timedelta(hours=7)