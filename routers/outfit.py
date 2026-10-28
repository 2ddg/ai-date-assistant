import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.vision_client import analyze_outfit
from database import get_db
from models.date_spot import OutfitImage
from security import get_current_user_id
from config import MAX_UPLOAD_BYTES, UPLOAD_DIR

router = APIRouter(prefix="/api/outfit", tags=["穿搭评价"])

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="仅支持 jpg/jpeg/png/webp 图片")

    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="图片不能超过 5MB")

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    image = OutfitImage(user_id=user_id, file_path=file_path)
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"image_id": image.id, "url": f"/uploads/{filename}"}


@router.post("/analyze")
async def analyze(
    image_id: int = 0,
    occasion: str = "",
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    image = db.get(OutfitImage, image_id)
    if image is None or image.user_id != user_id:
        raise HTTPException(status_code=404, detail="图片不存在")

    image.occasion = occasion
    result = await analyze_outfit(image.file_path, occasion or None)
    image.analysis_result = result
    db.commit()
    return {"analysis": result}


@router.get("/list")
async def list_images(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    images = (
        db.query(OutfitImage)
        .filter(OutfitImage.user_id == user_id)
        .order_by(OutfitImage.id.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": img.id,
            "url": f"/uploads/{os.path.basename(img.file_path)}",
            "occasion": img.occasion,
            "analysis": img.analysis_result,
            "time": img.created_at.isoformat(),
        }
        for img in images
    ]


@router.get("/{image_id}")
async def get_image_detail(
    image_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    image = db.get(OutfitImage, image_id)
    if image is None or image.user_id != user_id:
        raise HTTPException(status_code=404, detail="图片不存在")
    return {
        "id": image.id,
        "url": f"/uploads/{os.path.basename(image.file_path)}",
        "occasion": image.occasion,
        "analysis": image.analysis_result,
        "time": image.created_at.isoformat(),
    }
