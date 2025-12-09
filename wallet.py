from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
import models

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/me")
def get_wallet(db: Session = Depends(get_db), user=Depends(get_current_user)):
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user.id).first()
    if not wallet:
        wallet = models.Wallet(user_id=user.id, balance=0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return {"balance": wallet.balance}
