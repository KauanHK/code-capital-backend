import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, Service, Transaction
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _validate_references(db: Session, payload: TransactionCreate | TransactionUpdate) -> None:
    service = db.get(Service, payload.service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    if payload.client_id is not None:
        client = db.get(Client, payload.client_id)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)) -> Transaction:
    _validate_references(db, payload)

    transaction = Transaction(
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
def list_transactions(db: Session = Depends(get_db)) -> list[Transaction]:
    return db.scalars(select(Transaction).order_by(Transaction.created_at.desc())).all()


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    _validate_references(db, payload)

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
def delete_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
