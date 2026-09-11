from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, check_jurisdiction, RequestUser
from app.schemas.schemas import FieldPhotoResponse, FieldPhotoCreate, FieldPhotoUpdate
from app.services.photo_service import PhotoService

router = APIRouter()

@router.post("/photos/upload", response_model=FieldPhotoResponse, status_code=status.HTTP_201_CREATED, tags=["Photos"])
async def upload_field_photo_file(
    watershed_id: int = Form(...),
    category: str = Form("WATER_BODY"),
    description: Optional[str] = Form(None),
    intervention_id: Optional[int] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    uploader_role: str = Form("FIELD_SURVEYOR"),
    file: UploadFile = File(...),
    current_user: RequestUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Direct image upload endpoint.
    Automatically parses GPS coordinates and acquisition timestamp from EXIF metadata.
    Falls back to manual latitude/longitude if image lacks EXIF GPS tags.
    Enforces jurisdictional boundaries when authenticated.
    """
    if current_user.is_authenticated:
        check_jurisdiction(current_user, db, watershed_id=watershed_id)

    content = await file.read()
    try:
        return PhotoService.upload_field_photo_file(
            db=db,
            file_bytes=content,
            filename=file.filename or "field_photo.jpg",
            watershed_id=watershed_id,
            category=category,
            description=description,
            intervention_id=intervention_id,
            manual_lat=latitude,
            manual_lon=longitude,
            uploader_role=uploader_role
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/photos", response_model=FieldPhotoResponse, status_code=status.HTTP_201_CREATED, tags=["Photos"])
def upload_field_photo(
    photo_in: FieldPhotoCreate,
    db: Session = Depends(get_db)
):
    """Uploads a geo-tagged field photo record with coordinate validation (-90 to 90 lat, -180 to 180 lng)."""
    try:
        return PhotoService.create_field_photo(db, photo_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/photos", response_model=List[FieldPhotoResponse], tags=["Photos"])
def list_field_photos(
    watershed_id: Optional[int] = Query(None, description="Filter by Watershed ID"),
    category: Optional[str] = Query(None, description="Category filter (CHECK_DAM, DESILTATION, WATER_BODY, etc.)"),
    verification_status: Optional[str] = Query(None, description="Status filter (VERIFIED, PENDING, REJECTED)"),
    intervention_id: Optional[int] = Query(None, description="Filter by linked intervention ID"),
    source_type: Optional[str] = Query(None, description="Source filter (FIELD_UPLOAD, DEMO, OFFICIAL)"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """Fetches geo-tagged field verification photographs with multi-criteria filtering and pagination."""
    return PhotoService.list_photos(
        db,
        watershed_id=watershed_id,
        category=category,
        verification_status=verification_status,
        intervention_id=intervention_id,
        source_type=source_type,
        limit=limit,
        offset=offset
    )

@router.get("/photos/{photo_id}", response_model=FieldPhotoResponse, tags=["Photos"])
def get_field_photo(
    photo_id: int = Path(..., ge=1, description="Field Photo ID"),
    db: Session = Depends(get_db)
):
    """Retrieves single geo-tagged field photograph metadata and EXIF payload."""
    photo = PhotoService.get_photo_by_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail=f"Field photo with ID {photo_id} not found.")
    return photo

@router.post("/photos", response_model=FieldPhotoResponse, status_code=status.HTTP_201_CREATED, tags=["Photos"])
def upload_field_photo(
    photo_in: FieldPhotoCreate,
    db: Session = Depends(get_db)
):
    """Uploads a geo-tagged field photo record with coordinate validation (-90 to 90 lat, -180 to 180 lng)."""
    try:
        return PhotoService.create_field_photo(db, photo_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/photos/{photo_id}", response_model=FieldPhotoResponse, tags=["Photos"])
def update_field_photo(
    photo_id: int = Path(..., ge=1, description="Field Photo ID"),
    photo_update: FieldPhotoUpdate = ...,
    db: Session = Depends(get_db)
):
    """Updates verification status, classification, or linked intervention ID for a field photo."""
    updated = PhotoService.update_field_photo(db, photo_id, photo_update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Field photo with ID {photo_id} not found.")
    return updated

@router.delete("/photos/{photo_id}", status_code=status.HTTP_200_OK, tags=["Photos"])
def delete_field_photo(
    photo_id: int = Path(..., ge=1, description="Field Photo ID"),
    db: Session = Depends(get_db)
):
    """Deletes a field photo record."""
    success = PhotoService.delete_field_photo(db, photo_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Field photo with ID {photo_id} not found.")
    return {"status": "success", "message": f"Field photo {photo_id} deleted successfully."}
