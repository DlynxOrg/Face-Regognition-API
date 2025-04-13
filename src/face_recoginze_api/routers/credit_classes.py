from fastapi import APIRouter, Depends, HTTPException, status, FastAPI
from typing import List
from contextlib import asynccontextmanager
from face_recoginze_api.models.models import CreditClass
from face_recoginze_api.DTOs.dtos import CreditClassCreate, CreditClassRead
from face_recoginze_api.database.database import Database
from face_recoginze_api.repositories.credit_class_repository import CreditClassRepository
from face_recoginze_api.services.credit_class_service import CreditClassService

database = Database()
@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    print("Khởi tạo lifespan trong faces")
    async with database.get_session() as db_session:  # ✅ Dùng async with để lấy AsyncSession
        service = CreditClassService(session=db_session)
        yield  # Đợi FastAPI chạy app
        service = None  # Cleanup khi app shutdown

router = APIRouter(lifespan=lifespan)

@router.get("/", response_model=List[CreditClassRead])
async def list_credit_classes():
    return await service.list_credit_classes()

@router.get("/{id}", response_model=CreditClassRead)
async def get_credit_class(id: int):
    credit_class = await service.get_credit_class(id)
    if not credit_class:
        raise HTTPException(status_code=404, detail="Credit class not found")
    return credit_class

@router.post("/", response_model=CreditClassRead, status_code=status.HTTP_201_CREATED)
async def create_credit_class(
    data: CreditClassCreate
):
    return await service.create_credit_class(name=data.name)

@router.put("/{id}", response_model=CreditClassRead)
async def update_credit_class(
    id: int,
    data: CreditClassCreate
):
    credit_class = await service.update_credit_class(id, name=data.name)
    if not credit_class:
        raise HTTPException(status_code=404, detail="Credit class not found")
    return credit_class

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credit_class(id: int):
    deleted = await service.delete_credit_class(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Credit class not found")
