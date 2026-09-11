import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.domain import FieldPhoto, Watershed, Observation
from app.schemas.schemas import FieldPhotoCreate, FieldPhotoResponse, FieldPhotoUpdate
from app.core.spatial import validate_coordinates

class PhotoService:
    @staticmethod
    def get_photos_by_watershed(
        db: Session,
        watershed_id: int,
        category: Optional[str] = None,
        verification_status: Optional[str] = None
    ) -> List[FieldPhotoResponse]:
        """Backward-compatible method: fetches photos for a specific watershed."""
        return PhotoService.list_photos(
            db=db,
            watershed_id=watershed_id,
            category=category,
            verification_status=verification_status
        )

    @staticmethod
    def list_photos(
        db: Session,
        watershed_id: Optional[int] = None,
        category: Optional[str] = None,
        verification_status: Optional[str] = None,
        intervention_id: Optional[int] = None,
        source_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FieldPhotoResponse]:
        """Lists field photos with flexible filtering and pagination."""
        query = db.query(FieldPhoto)
        if watershed_id:
            query = query.filter(FieldPhoto.watershed_id == watershed_id)
        if category:
            query = query.filter(FieldPhoto.category == category.upper())
        if verification_status:
            query = query.filter(FieldPhoto.verification_status == verification_status.upper())
        if intervention_id:
            query = query.filter(FieldPhoto.intervention_id == intervention_id)
        if source_type:
            query = query.filter(FieldPhoto.source_type == source_type.upper())
            
        photos = query.order_by(FieldPhoto.captured_at.desc()).offset(offset).limit(limit).all()
        return [FieldPhotoResponse.model_validate(p) for p in photos]

    @staticmethod
    def get_photo_by_id(db: Session, photo_id: int) -> Optional[FieldPhotoResponse]:
        """Retrieves a single field photo record."""
        photo = db.query(FieldPhoto).filter(FieldPhoto.id == photo_id).first()
        if not photo:
            return None
        return FieldPhotoResponse.model_validate(photo)

    @staticmethod
    def create_field_photo(db: Session, photo_in: FieldPhotoCreate) -> FieldPhotoResponse:
        """Uploads and validates a geo-tagged field photo record."""
        # Validate coordinates
        is_valid, err = validate_coordinates(photo_in.latitude, photo_in.longitude)
        if not is_valid:
            raise ValueError(err)

        # Check watershed exists
        ws = db.query(Watershed).filter(Watershed.id == photo_in.watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed ID {photo_in.watershed_id} does not exist.")

        # Coordinate extraction from EXIF if present
        lat = photo_in.latitude
        lng = photo_in.longitude
        if photo_in.exif_metadata and "gps_latitude" in photo_in.exif_metadata:
            lat = float(photo_in.exif_metadata["gps_latitude"])
            lng = float(photo_in.exif_metadata.get("gps_longitude", lng))

        photo = FieldPhoto(
            watershed_id=photo_in.watershed_id,
            latitude=lat,
            longitude=lng,
            captured_at=datetime.datetime.utcnow(),
            uploaded_at=datetime.datetime.utcnow(),
            photo_url=photo_in.photo_url,
            category=photo_in.category.upper(),
            description=photo_in.description,
            intervention_id=photo_in.intervention_id,
            verification_status="PENDING",
            source_type="FIELD_UPLOAD",
            exif_metadata=photo_in.exif_metadata or {},
            uploader_role=photo_in.uploader_role or "FIELD_OFFICER"
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return FieldPhotoResponse.model_validate(photo)

    @staticmethod
    def update_field_photo(
        db: Session, 
        photo_id: int, 
        photo_update: FieldPhotoUpdate
    ) -> Optional[FieldPhotoResponse]:
        """Updates metadata, verification status, or intervention link for a field photo."""
        photo = db.query(FieldPhoto).filter(FieldPhoto.id == photo_id).first()
        if not photo:
            return None

        if photo_update.category is not None:
            photo.category = photo_update.category.upper()
        if photo_update.description is not None:
            photo.description = photo_update.description
        if photo_update.verification_status is not None:
            photo.verification_status = photo_update.verification_status.upper()
        if photo_update.intervention_id is not None:
            photo.intervention_id = photo_update.intervention_id

        db.commit()
        db.refresh(photo)
        return FieldPhotoResponse.model_validate(photo)

    @staticmethod
    def delete_field_photo(db: Session, photo_id: int) -> bool:
        """Deletes a field photo record."""
        photo = db.query(FieldPhoto).filter(FieldPhoto.id == photo_id).first()
        if not photo:
            return False
        db.delete(photo)
        db.commit()
        return True

    @staticmethod
    def upload_field_photo_file(
        db: Session,
        file_bytes: bytes,
        filename: str,
        watershed_id: int,
        category: str = "WATER_BODY",
        description: Optional[str] = None,
        intervention_id: Optional[int] = None,
        manual_lat: Optional[float] = None,
        manual_lon: Optional[float] = None,
        uploader_role: str = "FIELD_SURVEYOR"
    ) -> FieldPhotoResponse:
        """Uploads a raw image file, auto-extracts EXIF GPS metadata if available, and stores record."""
        import os
        import uuid
        from app.core.exif import ExifExtractor

        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed ID {watershed_id} does not exist.")

        # Extract EXIF GPS
        exif_info = ExifExtractor.extract_from_bytes(file_bytes)
        lat = exif_info.get("latitude") if exif_info.get("has_gps") else manual_lat
        lon = exif_info.get("longitude") if exif_info.get("has_gps") else manual_lon

        if lat is None or lon is None:
            raise ValueError(
                "Image does not contain GPS location in EXIF tags. "
                "Please provide manual latitude and longitude parameters."
            )

        is_valid, err = validate_coordinates(lat, lon)
        if not is_valid:
            raise ValueError(err)

        # Save photo file
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "photos")
        os.makedirs(upload_dir, exist_ok=True)
        safe_filename = f"{uuid.uuid4().hex[:8]}_{filename.replace(' ', '_')}"
        file_path = os.path.join(upload_dir, safe_filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        photo_url = f"/uploads/photos/{safe_filename}"

        photo = FieldPhoto(
            watershed_id=watershed_id,
            latitude=lat,
            longitude=lon,
            captured_at=datetime.datetime.utcnow(),
            uploaded_at=datetime.datetime.utcnow(),
            photo_url=photo_url,
            category=category.upper(),
            description=description or f"Field photo uploaded by {uploader_role}",
            intervention_id=intervention_id,
            verification_status="VERIFIED" if exif_info.get("has_gps") else "PENDING",
            source_type="FIELD_UPLOAD",
            provenance="IMPORTED_DATA",
            exif_metadata=exif_info,
            uploader_role=uploader_role
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return FieldPhotoResponse.model_validate(photo)

