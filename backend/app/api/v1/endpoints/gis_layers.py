from typing import List, Optional, Union, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import (
    GISLayerResponse, GISLayerSummary, WatershedGISStatsResponse
)
from app.services.gis_service import GISService

router = APIRouter()

@router.get("/layers", response_model=Union[List[GISLayerResponse], List[GISLayerSummary]], tags=["GIS Layers"])
def get_gis_layers(
    watershed_id: Optional[int] = Query(None, description="Watershed ID filter"),
    layer_type: Optional[str] = Query(None, description="Optional layer type: BOUNDARY, DRAINAGE, WATER_BODIES, LULC, VEGETATION_NDVI, ELEVATION, etc."),
    summary_only: bool = Query(False, description="Set True to receive lightweight metadata without large GeoJSON geometries"),
    db: Session = Depends(get_db)
):
    """
    Retrieves GIS layers. Supports summary metadata mode to avoid transferring large geometry
    payloads when only catalog statistics are required.
    """
    if summary_only:
        return GISService.get_layers_summary(db, watershed_id=watershed_id, layer_type=layer_type)
    
    if watershed_id is None:
        # Default to all layers summary if no watershed is specified and full payload requested
        return GISService.get_layers_summary(db, layer_type=layer_type)

    return GISService.get_layers_for_watershed(db, watershed_id=watershed_id, layer_type=layer_type)

@router.get("/watersheds/{watershed_id}/layers", response_model=List[GISLayerResponse], tags=["GIS Layers"])
def get_watershed_layers(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    layer_type: Optional[str] = Query(None, description="Filter by layer type: BOUNDARY, DRAINAGE, WATER_BODIES, LULC, VEGETATION_NDVI, ELEVATION"),
    db: Session = Depends(get_db)
):
    """Dedicated endpoint retrieving all active vector/raster GIS layers for a given watershed."""
    return GISService.get_layers_for_watershed(db, watershed_id=watershed_id, layer_type=layer_type)

@router.get("/watersheds/{watershed_id}/layers/{layer_type}", response_model=GISLayerResponse, tags=["GIS Layers"])
def get_watershed_single_layer(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    layer_type: str = Path(..., description="Layer type: BOUNDARY, DRAINAGE, WATER_BODIES, LULC, VEGETATION_NDVI, ELEVATION"),
    db: Session = Depends(get_db)
):
    """Retrieves a single specific thematic GIS layer for the watershed."""
    layer = GISService.get_single_layer(db, watershed_id=watershed_id, layer_type=layer_type)
    if not layer:
        raise HTTPException(
            status_code=404,
            detail=f"Layer '{layer_type.upper()}' for watershed ID {watershed_id} not found."
        )
    return layer

@router.get("/watersheds/{watershed_id}/gis-stats", response_model=WatershedGISStatsResponse, tags=["GIS Layers"])
def get_watershed_gis_stats(
    watershed_id: int = Path(..., ge=1, description="Watershed ID"),
    db: Session = Depends(get_db)
):
    """
    Calculates unified geospatial indicators: LULC breakdown, drainage network density,
    surface water body storage capacity (TCM), NDVI biomass vigor, and elevation relief.
    """
    try:
        return GISService.calculate_watershed_gis_stats(db, watershed_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
