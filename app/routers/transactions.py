import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, Service, Transaction, User
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.security import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _validate_references(db: Session, payload: TransactionCreate | TransactionUpdate, current_user: User) -> None:
    service = db.scalar(
        select(Service).where(Service.id == payload.service_id, Service.user_id == current_user.id)
    )
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    if payload.client_id is not None:
        client = db.scalar(
            select(Client).where(Client.id == payload.client_id, Client.user_id == current_user.id)
        )
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    _validate_references(db, payload, current_user)

    transaction = Transaction(
        user_id=current_user.id,
        client_id=payload.client_id,
        service_id=payload.service_id,
        is_expense=payload.is_expense,
        is_personal=payload.is_personal,
        pjpf=payload.pjpf,
        amount=payload.amount,
        description=payload.description,
        status=payload.status,
        payment_method=payload.payment_method,
        transaction_date=payload.transaction_date,
    )

    db.add(transaction)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create transaction")

    db.refresh(transaction)
    return transaction


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    status_filter: Literal["pending", "paid", "cancelled"] | None = Query(default=None, alias="status"),
    is_expense: bool | None = None,
    is_personal: bool | None = None,
    pjpf: Literal["pj", "pf"] | None = None,
    client_id: uuid.UUID | None = None,
    service_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Transaction]:
    query = select(Transaction).where(Transaction.user_id == current_user.id)

    if status_filter is not None:
        query = query.where(Transaction.status == status_filter)
    if is_expense is not None:
        query = query.where(Transaction.is_expense == is_expense)
    if is_personal is not None:
        query = query.where(Transaction.is_personal == is_personal)
    if pjpf is not None:
        query = query.where(Transaction.pjpf == pjpf)
    if client_id is not None:
        query = query.where(Transaction.client_id == client_id)
    if service_id is not None:
        query = query.where(Transaction.service_id == service_id)

    return db.scalars(query.order_by(Transaction.created_at.desc())).all()


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    transaction = db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
    )
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    transaction = db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
    )
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    _validate_references(db, payload, current_user)

    transaction.client_id = payload.client_id
    transaction.service_id = payload.service_id
    transaction.is_expense = payload.is_expense
    transaction.is_personal = payload.is_personal
    transaction.pjpf = payload.pjpf
    transaction.amount = payload.amount
    transaction.description = payload.description
    transaction.status = payload.status
    transaction.payment_method = payload.payment_method
    transaction.transaction_date = payload.transaction_date

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update transaction")

    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    transaction = db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
    )
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
