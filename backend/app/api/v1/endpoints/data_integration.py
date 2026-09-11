"""
JalDrishti AI — Data Integration & Ingestion API Endpoints
Provides endpoints for GeoJSON/CSV ingestion, satellite provider adapter reporting,
dataset catalog discovery, and transparent provenance inspection.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import GeospatialDataset, DataIngestionJob, Watershed
from app.schemas.schemas import (
    GeospatialDatasetResponse, DatasetCatalogResponse,
    DataIngestionJobResponse, ProviderAdapterResponse
)
from app.data_pipeline.importer import DataImporter
from app.data_pipeline.normalizer import DataNormalizer
from app.integrations.registry import ProviderRegistry

router = APIRouter()

@router.get("/catalog", response_model=DatasetCatalogResponse, summary="Catalog of registered geospatial datasets")
def get_dataset_catalog(
    watershed_id: Optional[int] = Query(None, description="Filter by watershed ID"),
    dataset_type: Optional[str] = Query(None, description="Filter by dataset type (LULC, DRAINAGE, FIELD_PHOTOS, etc.)"),
    provenance: Optional[str] = Query(None, description="Filter by provenance (DEMO_DATA, IMPORTED_DATA, OFFICIAL_SOURCE)"),
    db: Session = Depends(get_db)
):
    query = db.query(GeospatialDataset)
    if watershed_id:
        query = query.filter(GeospatialDataset.watershed_id == watershed_id)
    if dataset_type:
        query = query.filter(GeospatialDataset.dataset_type == dataset_type.upper())
    if provenance:
        query = query.filter(GeospatialDataset.provenance == provenance.upper())

    datasets = query.order_by(GeospatialDataset.created_at.desc()).all()
    
    total = len(datasets)
    demo_count = sum(1 for d in datasets if d.provenance == "DEMO_DATA")
    imported_count = sum(1 for d in datasets if d.provenance == "IMPORTED_DATA")
    official_count = sum(1 for d in datasets if d.provenance == "OFFICIAL_SOURCE")

    summary = {
        "total_datasets": total,
        "demo_datasets_count": demo_count,
        "imported_datasets_count": imported_count,
        "official_source_count": official_count,
        "active_watershed_filter": watershed_id
    }

    return DatasetCatalogResponse(
        total_datasets=total,
        datasets=[GeospatialDatasetResponse.model_validate(d) for d in datasets],
        provenance_summary=summary
    )

@router.get("/adapters", response_model=List[ProviderAdapterResponse], summary="Authoritative satellite & GIS provider adapters")
def get_provider_adapters():
    """
    Returns registered multi-constellation Earth Observation adapters
    (Sentinel-2 CDSE, USGS Landsat, NRSC Bhuvan) and their connection readiness.
    """
    return [ProviderAdapterResponse.model_validate(a) for a in ProviderRegistry.list_adapters()]

@router.get("/provenance/{watershed_id}", summary="Active data provenance summary for a watershed")
def get_watershed_provenance(
    watershed_id: int,
    db: Session = Depends(get_db)
):
    ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail=f"Watershed ID {watershed_id} not found.")

    return DataNormalizer.get_watershed_provenance_summary(db, watershed_id)

@router.post("/import/geojson", summary="Import real GeoJSON vector layer")
async def import_geojson_layer(
    watershed_id: int = Form(...),
    layer_type: str = Form(..., description="LULC, DRAINAGE, WATER_BODIES, INTERVENTIONS, BOUNDARY"),
    dataset_name: Optional[str] = Form(None),
    provider: str = Form("Field Survey Upload"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Safely ingests and validates a GeoJSON vector layer.
    Validates geometry topology, checks coordinates, and updates the GIS layer with IMPORTED_DATA provenance.
    """
    content = await file.read()
    try:
        result = DataImporter.import_geojson(
            db=db,
            geojson_data=content,
            watershed_id=watershed_id,
            layer_type=layer_type,
            dataset_name=dataset_name,
            provider=provider
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/import/csv", summary="Import coordinate CSV dataset")
async def import_csv_dataset(
    watershed_id: int = Form(...),
    dataset_type: str = Form("FIELD_PHOTOS", description="FIELD_PHOTOS, OBSERVATIONS, or INDICATORS"),
    dataset_name: Optional[str] = Form(None),
    provider: str = Form("Field Ground Team"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Safely ingests and validates a coordinate CSV dataset.
    Validates latitude/longitude coordinates and creates verified field records with IMPORTED_DATA provenance.
    """
    content = await file.read()
    try:
        result = DataImporter.import_csv(
            db=db,
            csv_content=content,
            watershed_id=watershed_id,
            dataset_type=dataset_type,
            dataset_name=dataset_name,
            provider=provider
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV Ingestion failed: {str(e)}")

@router.get("/jobs/{job_id}", response_model=DataIngestionJobResponse, summary="Inspect status of an ingestion job")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(DataIngestionJob).filter(DataIngestionJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job ID '{job_id}' not found.")
    return DataIngestionJobResponse.model_validate(job)
