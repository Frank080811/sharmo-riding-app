from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import os
import shutil
from auth import get_current_user
import models

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/drivers/upload-document")
async def upload_doc(
    doc: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
):
    if user.role != models.UserRole.driver:
        raise HTTPException(status_code=403, detail="Only drivers can upload documents")
    filename = f"{user.id}_{doc.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(doc.file, buffer)
    return {"message": "Uploaded", "file": filename}
