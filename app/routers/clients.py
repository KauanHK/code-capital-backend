import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, Transaction, User
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.security import get_current_user

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Client:
    client = Client(
        user_id=current_user.id,
        name=payload.name,
        cpf_cnpj=payload.cpf_cnpj,
        email=payload.email,
        phone=payload.phone,
        type=payload.type,
    )
    db.add(client)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create client")

    db.refresh(client)
    return client


@router.get("", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Client]:
    return db.scalars(
        select(Client).where(Client.user_id == current_user.id).order_by(Client.created_at.desc())
    ).all()


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Client:
    client = db.scalar(select(Client).where(Client.id == client_id, Client.user_id == current_user.id))
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Client:
    client = db.scalar(select(Client).where(Client.id == client_id, Client.user_id == current_user.id))
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    client.name = payload.name
    client.cpf_cnpj = payload.cpf_cnpj
    client.email = payload.email
    client.phone = payload.phone
    client.type = payload.type

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update client")

    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    client = db.scalar(select(Client).where(Client.id == client_id, Client.user_id == current_user.id))
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    has_transactions = db.scalar(
        select(Transaction.id)
        .where(Transaction.client_id == client_id, Transaction.user_id == current_user.id)
        .limit(1)
    )
    if has_transactions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client has related transactions and cannot be deleted",
        )

    db.delete(client)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
