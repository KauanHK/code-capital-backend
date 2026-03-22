from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRead
from app.security import get_admin_only

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserRead, status_code=status.HTTP_200_OK)
def get_user_by_number(
    number: str = Query(..., min_length=1, max_length=50, description="User number"),
    db: Session = Depends(get_db),
    _: bool = Depends(get_admin_only),
):
    """
    Get user by their number. Only admins can access this endpoint.
    
    **Admin Token Required**
    
    Query Parameters:
    - number: The user's number
    
    Returns: User information (id, username, number, created_at)
    
    Raises:
    - 401: Invalid admin token
    - 403: Not an admin token
    - 404: User not found with that number
    """
    user = db.scalar(select(User).where(User.number == number))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with number '{number}' not found",
        )
    
    return user
