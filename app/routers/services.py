import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Service, Transaction, User
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.security import get_current_user

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Service:
    category = db.scalar(
        select(Category).where(Category.id == payload.category_id, Category.user_id == current_user.id)
    )
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    service = Service(name=payload.name, category_id=payload.category_id, user_id=current_user.id)
    db.add(service)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create service")

    db.refresh(service)
    return service


@router.get("", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Service]:
    return db.scalars(select(Service).where(Service.user_id == current_user.id).order_by(Service.name.asc())).all()


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Service:
    service = db.scalar(select(Service).where(Service.id == service_id, Service.user_id == current_user.id))
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


@router.put("/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Service:
    service = db.scalar(select(Service).where(Service.id == service_id, Service.user_id == current_user.id))
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    category = db.scalar(
        select(Category).where(Category.id == payload.category_id, Category.user_id == current_user.id)
    )
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    service.name = payload.name
    service.category_id = payload.category_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update service")

    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    service = db.scalar(select(Service).where(Service.id == service_id, Service.user_id == current_user.id))
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    has_transactions = db.scalar(
        select(Transaction.id)
        .where(Transaction.service_id == service_id, Transaction.user_id == current_user.id)
        .limit(1)
    )
    if has_transactions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service has related transactions and cannot be deleted",
        )

    db.delete(service)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
