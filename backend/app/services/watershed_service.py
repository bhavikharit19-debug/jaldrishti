from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.domain import Watershed, WatershedBoundary, State, District
from app.schemas.schemas import (
    WatershedListItem, WatershedDetail, StateResponse, DistrictResponse,
    StateListItem, DistrictListItem, WatershedLocateResult, WatershedBoundaryResponse
)
from app.core.spatial import (
    point_in_geojson_geometry, bbox_intersects,
    calculate_haversine_distance_km, validate_coordinates
)

class WatershedService:
    @staticmethod
    def get_states_hierarchy(db: Session) -> List[StateResponse]:
        """Returns State -> District hierarchical tree for cascading dropdowns."""
        states = db.query(State).all()
        return [StateResponse.model_validate(s) for s in states]

    @staticmethod
    def list_states(
        db: Session,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StateListItem]:
        """Lists all administrative states with district and watershed counts."""
        query = db.query(State)
        if search:
            query = query.filter(State.name.ilike(f"%{search}%") | State.code.ilike(f"%{search}%"))
        
        states = query.order_by(State.name).offset(offset).limit(limit).all()
        result = []
        for s in states:
            d_count = len(s.districts) if s.districts else 0
            ws_count = len(s.watersheds) if s.watersheds else 0
            result.append(StateListItem(
                id=s.id,
                name=s.name,
                code=s.code,
                district_count=d_count,
                watershed_count=ws_count
            ))
        return result

    @staticmethod
    def get_state_by_id(db: Session, state_id: int) -> Optional[StateResponse]:
        """Retrieves single state with its child districts."""
        state = db.query(State).filter(State.id == state_id).first()
        if not state:
            return None
        return StateResponse.model_validate(state)

    @staticmethod
    def list_districts(
        db: Session,
        state_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[DistrictListItem]:
        """Lists districts with optional state filter and text search."""
        query = db.query(District)
        if state_id:
            query = query.filter(District.state_id == state_id)
        if search:
            query = query.filter(District.name.ilike(f"%{search}%") | District.code.ilike(f"%{search}%"))
        
        districts = query.order_by(District.name).offset(offset).limit(limit).all()
        result = []
        for d in districts:
            ws_count = len(d.watersheds) if d.watersheds else 0
            result.append(DistrictListItem(
                id=d.id,
                name=d.name,
                code=d.code,
                state_id=d.state_id,
                state_name=d.state.name if d.state else None,
                watershed_count=ws_count
            ))
        return result

    @staticmethod
    def get_district_by_id(db: Session, district_id: int) -> Optional[DistrictListItem]:
        """Retrieves single district detail."""
        d = db.query(District).filter(District.id == district_id).first()
        if not d:
            return None
        return DistrictListItem(
            id=d.id,
            name=d.name,
            code=d.code,
            state_id=d.state_id,
            state_name=d.state.name if d.state else None,
            watershed_count=len(d.watersheds) if d.watersheds else 0
        )

    @staticmethod
    def list_districts_for_state(db: Session, state_id: int) -> List[DistrictResponse]:
        """Lists all districts belonging to a specific state."""
        districts = db.query(District).filter(District.state_id == state_id).order_by(District.name).all()
        return [DistrictResponse.model_validate(d) for d in districts]

    @staticmethod
    def list_watersheds_for_district(db: Session, district_id: int) -> List[WatershedListItem]:
        """Lists all watersheds belonging to a specific district."""
        return WatershedService.list_watersheds(db, district_id=district_id)

    @staticmethod
    def list_watersheds(
        db: Session,
        state_id: Optional[int] = None,
        district_id: Optional[int] = None,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        min_lng: Optional[float] = None,
        min_lat: Optional[float] = None,
        max_lng: Optional[float] = None,
        max_lat: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WatershedListItem]:
        """Lists all watersheds with multi-criteria administrative, status, and spatial bounding-box filtering."""
        query = db.query(Watershed)
        
        if state_id:
            query = query.filter(Watershed.state_id == state_id)
        if district_id:
            query = query.filter(Watershed.district_id == district_id)
        if risk_level:
            query = query.filter(Watershed.risk_level == risk_level.upper())
        if status:
            query = query.filter(Watershed.status == status.upper())
        if search:
            query = query.filter(Watershed.name.ilike(f"%{search}%") | Watershed.code.ilike(f"%{search}%"))
            
        watersheds = query.order_by(Watershed.id).offset(offset).limit(limit).all()
        
        # Apply spatial bounding-box filter if coordinates provided
        has_bbox = (
            min_lng is not None and min_lat is not None and
            max_lng is not None and max_lat is not None
        )
        filter_bbox = [min_lng, min_lat, max_lng, max_lat] if has_bbox else None
        
        result = []
        for ws in watersheds:
            if filter_bbox and ws.boundary and ws.boundary.bbox:
                if not bbox_intersects(ws.boundary.bbox, filter_bbox):
                    continue
            
            item = WatershedListItem(
                id=ws.id,
                code=ws.code,
                name=ws.name,
                district_id=ws.district_id,
                district_name=ws.district.name if ws.district else None,
                state_id=ws.state_id,
                state_name=ws.state.name if ws.state else None,
                area_hectares=ws.area_hectares,
                health_score=ws.health_score,
                risk_level=ws.risk_level,
                status=ws.status
            )
            result.append(item)
        return result

    @staticmethod
    def get_watershed_by_id(db: Session, watershed_id: int) -> Optional[WatershedDetail]:
        """Retrieves full details of a specific watershed including boundary geometry and metadata."""
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            return None
            
        boundary_resp = None
        if ws.boundary:
            boundary_resp = WatershedBoundaryResponse.model_validate(ws.boundary)

        return WatershedDetail(
            id=ws.id,
            code=ws.code,
            name=ws.name,
            district_id=ws.district_id,
            district_name=ws.district.name if ws.district else None,
            state_id=ws.state_id,
            state_name=ws.state.name if ws.state else None,
            area_hectares=ws.area_hectares,
            river_basin=ws.river_basin,
            sub_basin=ws.sub_basin,
            agro_climatic_zone=ws.agro_climatic_zone,
            primary_drainage=ws.primary_drainage,
            health_score=ws.health_score,
            risk_level=ws.risk_level,
            status=ws.status,
            boundary=boundary_resp
        )

    @staticmethod
    def get_watershed_boundary(db: Session, watershed_id: int) -> Optional[Dict[str, Any]]:
        """Returns the GeoJSON Feature of the watershed boundary."""
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws or not ws.boundary:
            return None
        
        return {
            "type": "Feature",
            "properties": {
                "watershed_id": ws.id,
                "watershed_name": ws.name,
                "watershed_code": ws.code,
                "area_hectares": ws.area_hectares,
                "centroid": [ws.boundary.centroid_lng, ws.boundary.centroid_lat],
                "bbox": ws.boundary.bbox
            },
            "geometry": ws.boundary.geometry
        }

    @staticmethod
    def locate_watershed_by_coordinates(db: Session, latitude: float, longitude: float) -> Optional[WatershedLocateResult]:
        """
        Locates the watershed containing the given GPS point using Shapely polygon containment.
        If the point is slightly outside boundaries, returns the nearest watershed with proximity distance.
        """
        valid, err = validate_coordinates(latitude, longitude)
        if not valid:
            raise ValueError(err)

        boundaries = db.query(WatershedBoundary).all()
        nearest_ws = None
        min_dist_km = float('inf')
        inside_ws = None

        for b in boundaries:
            ws = b.watershed
            if not ws:
                continue
            
            # Check point-in-polygon containment
            if b.geometry and point_in_geojson_geometry(latitude, longitude, b.geometry):
                inside_ws = ws
                nearest_ws = ws
                min_dist_km = calculate_haversine_distance_km(latitude, longitude, b.centroid_lat, b.centroid_lng)
                break
            
            # Calculate distance to centroid
            dist = calculate_haversine_distance_km(latitude, longitude, b.centroid_lat, b.centroid_lng)
            if dist < min_dist_km:
                min_dist_km = dist
                nearest_ws = ws

        target = inside_ws or nearest_ws
        if not target or not target.boundary:
            return None

        return WatershedLocateResult(
            watershed_id=target.id,
            watershed_name=target.name,
            watershed_code=target.code,
            district_name=target.district.name if target.district else "Unknown",
            state_name=target.state.name if target.state else "Unknown",
            is_inside=(inside_ws is not None),
            distance_to_centroid_km=round(min_dist_km, 2),
            centroid_lat=target.boundary.centroid_lat,
            centroid_lng=target.boundary.centroid_lng
        )
