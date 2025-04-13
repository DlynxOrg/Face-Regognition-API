from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from face_recoginze_api.models.models import CreditClass
from face_recoginze_api.DTOs.dtos import CreditClassCreate, CreditClassRead
from face_recoginze_api.database.database import Database
from face_recoginze_api.repositories.credit_class_repository import CreditClassRepository
from face_recoginze_api.services.credit_class_service import CreditClassService

router = APIRouter()
database = Database()

def get_service(session: AsyncSession = Depends(database.get_session)) -> CreditClassService:
    repo = CreditClassRepository(session)
    return CreditClassService(repo)

@router.get("/", response_model=List[CreditClassRead])
async def list_credit_classes(service: CreditClassService = Depends(get_service)):
    return await service.list_credit_classes()

@router.get("/{id}", response_model=CreditClassRead)
async def get_credit_class(id: int, service: CreditClassService = Depends(get_service)):
    credit_class = await service.get_credit_class(id)
    if not credit_class:
        raise HTTPException(status_code=404, detail="Credit class not found")
    return credit_class

@router.post("/", response_model=CreditClassRead, status_code=status.HTTP_201_CREATED)
async def create_credit_class(
    data: CreditClassCreate,
    service: CreditClassService = Depends(get_service)
):
    return await service.create_credit_class(name=data.name)

@router.put("/{id}", response_model=CreditClassRead)
async def update_credit_class(
    id: int,
    data: CreditClassCreate,
    service: CreditClassService = Depends(get_service)
):
    credit_class = await service.update_credit_class(id, name=data.name)
    if not credit_class:
        raise HTTPException(status_code=404, detail="Credit class not found")
    return credit_class

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credit_class(id: int, service: CreditClassService = Depends(get_service)):
    deleted = await service.delete_credit_class(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Credit class not found")
