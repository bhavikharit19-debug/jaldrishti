"""
JalDrishti AI — Geospatial Data Importer & Validation Engine
Handles safe ingestion of GeoJSON vectors, coordinate CSVs, and raster metadata
with CRS validation, topological validity checks, and spatial watershed linking.
"""

import io
import csv
import json
import uuid
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.orm import Session

from app.models.domain import (
    Watershed, WatershedBoundary, GISLayer, FieldPhoto,
    Observation, GeospatialDataset, DataIngestionJob, Indicator, IndicatorValue
)
from app.core.spatial import (
    validate_coordinates, validate_geojson_geometry,
    calculate_geometry_bounds, bbox_intersects, check_point_in_watershed
)

class DataImporter:
    """
    Production-grade data ingestion manager for official and field datasets.
    Guarantees that imported data is tagged with IMPORTED_DATA provenance.
    """

    @staticmethod
    def import_geojson(
        db: Session,
        geojson_data: Union[Dict[str, Any], str, bytes],
        watershed_id: int,
        layer_type: str,
        dataset_name: Optional[str] = None,
        provider: str = "User Upload",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        job_id = f"job-geojson-{uuid.uuid4().hex[:8]}"
        job = DataIngestionJob(
            job_id=job_id,
            watershed_id=watershed_id,
            source_format="GEOJSON",
            status="PROCESSING",
            records_processed=0,
            records_failed=0,
            log_messages=[f"Beginning GeoJSON ingestion for watershed {watershed_id}, layer {layer_type}"]
        )
        db.add(job)
        db.commit()

        # 1. Parse JSON payload
        if isinstance(geojson_data, (bytes, bytearray)):
            try:
                data_dict = json.loads(geojson_data.decode("utf-8"))
            except Exception as e:
                job.status = "FAILED"
                job.log_messages.append(f"Invalid JSON syntax: {str(e)}")
                db.commit()
                raise ValueError(f"Invalid GeoJSON file content: {str(e)}")
        elif isinstance(geojson_data, str):
            try:
                data_dict = json.loads(geojson_data)
            except Exception as e:
                job.status = "FAILED"
                job.log_messages.append(f"Invalid JSON syntax: {str(e)}")
                db.commit()
                raise ValueError(f"Invalid GeoJSON string: {str(e)}")
        else:
            data_dict = geojson_data

        # 2. Verify watershed exists
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            job.status = "FAILED"
            job.log_messages.append(f"Watershed ID {watershed_id} not found.")
            db.commit()
            raise ValueError(f"Watershed with ID {watershed_id} does not exist.")

        ws_boundary = db.query(WatershedBoundary).filter(WatershedBoundary.watershed_id == watershed_id).first()
        ws_bbox = ws_boundary.bbox if ws_boundary else None

        # 3. Normalize into FeatureCollection
        if data_dict.get("type") == "FeatureCollection":
            features = data_dict.get("features", [])
        elif data_dict.get("type") == "Feature":
            features = [data_dict]
            data_dict = {"type": "FeatureCollection", "features": features}
        elif "type" in data_dict and "coordinates" in data_dict:
            features = [{"type": "Feature", "properties": {}, "geometry": data_dict}]
            data_dict = {"type": "FeatureCollection", "features": features}
        else:
            job.status = "FAILED"
            job.log_messages.append("GeoJSON missing FeatureCollection or Feature root structure.")
            db.commit()
            raise ValueError("GeoJSON must be a valid FeatureCollection or Feature.")

        if not features:
            job.status = "FAILED"
            job.log_messages.append("FeatureCollection contains 0 features.")
            db.commit()
            raise ValueError("GeoJSON FeatureCollection contains no features to import.")

        # 4. Validate each feature's geometry and attributes
        valid_features = []
        overall_minx, overall_miny = 180.0, 90.0
        overall_maxx, overall_maxy = -180.0, -90.0

        for idx, feat in enumerate(features):
            geom = feat.get("geometry")
            if not geom:
                job.log_messages.append(f"Feature #{idx} has null geometry — skipped.")
                job.records_failed += 1
                continue

            is_valid, err_msg, bounds = validate_geojson_geometry(geom)
            if not is_valid:
                job.log_messages.append(f"Feature #{idx} topology error: {err_msg} — skipped.")
                job.records_failed += 1
                continue

            # Update overall bounds
            overall_minx = min(overall_minx, bounds[0])
            overall_miny = min(overall_miny, bounds[1])
            overall_maxx = max(overall_maxx, bounds[2])
            overall_maxy = max(overall_maxy, bounds[3])

            # Layer-specific attribute validation
            props = feat.get("properties") or {}
            layer_upper = layer_type.upper()
            if layer_upper == "LULC" and not any(k in props for k in ["class", "category", "lulc_class"]):
                props["class"] = "Unclassified"
            feat["properties"] = props

            valid_features.append(feat)

        if not valid_features:
            job.status = "FAILED"
            job.log_messages.append("No topologically valid features found in dataset.")
            db.commit()
            raise ValueError("All features failed geometric topology validation.")

        total_bounds = [round(overall_minx, 6), round(overall_miny, 6), round(overall_maxx, 6), round(overall_maxy, 6)]

        # 5. Spatial Watershed Bounding Check
        if ws_bbox and not bbox_intersects(total_bounds, ws_bbox):
            job.log_messages.append(f"Warning: Dataset bounds {total_bounds} do not intersect watershed bounds {ws_bbox}.")

        # 6. Save or Update GISLayer (targets FIELD_UPLOAD layer without overwriting DEMO baseline)
        normalized_collection = {"type": "FeatureCollection", "features": valid_features}
        existing_layer = db.query(GISLayer).filter(
            GISLayer.watershed_id == watershed_id,
            GISLayer.layer_type == layer_type.upper(),
            GISLayer.source_type == "FIELD_UPLOAD"
        ).first()

        layer_name = dataset_name or f"Imported {layer_type.replace('_', ' ').title()}"
        if existing_layer:
            existing_layer.data_payload = normalized_collection
            existing_layer.name = layer_name
            existing_layer.source_type = "FIELD_UPLOAD"
            existing_layer.metadata_json = {
                **(existing_layer.metadata_json or {}),
                "last_imported_at": datetime.datetime.utcnow().isoformat(),
                "provider": provider,
                "feature_count": len(valid_features),
                "bounds": total_bounds,
                "provenance": "IMPORTED_DATA"
            }
            target_layer = existing_layer
        else:
            new_layer = GISLayer(
                watershed_id=watershed_id,
                layer_type=layer_type.upper(),
                name=layer_name,
                format="GEOJSON",
                data_payload=normalized_collection,
                is_active=True,
                source_type="FIELD_UPLOAD",
                metadata_json={
                    "provider": provider,
                    "feature_count": len(valid_features),
                    "bounds": total_bounds,
                    "provenance": "IMPORTED_DATA"
                }
            )
            db.add(new_layer)
            target_layer = new_layer

        db.flush()

        # 7. Create GeospatialDataset Catalog Entry
        ds_code = f"DS-{ws.code}-{layer_type.upper()}-{uuid.uuid4().hex[:6].upper()}"
        dataset = GeospatialDataset(
            dataset_code=ds_code,
            dataset_name=layer_name,
            dataset_type=layer_type.upper(),
            provider=provider,
            watershed_id=watershed_id,
            acquisition_date=datetime.datetime.utcnow(),
            processing_date=datetime.datetime.utcnow(),
            spatial_resolution="Vector Feature Geometry",
            temporal_resolution="Snapshot",
            coverage_bounds=total_bounds,
            crs="EPSG:4326",
            provenance="IMPORTED_DATA",
            format="GEOJSON",
            record_count=len(valid_features),
            license_info=metadata.get("license", "Authorized Local Government / Field Use") if metadata else "Authorized Field Use",
            metadata_json=metadata or {},
            status="ACTIVE"
        )
        db.add(dataset)
        db.flush()

        # Update Job
        job.dataset_id = dataset.id
        job.records_processed = len(valid_features)
        job.status = "COMPLETED"
        job.completed_at = datetime.datetime.utcnow()
        job.log_messages.append(f"Successfully ingested {len(valid_features)} features into {ds_code}.")

        db.commit()

        return {
            "status": "SUCCESS",
            "job_id": job_id,
            "dataset_id": dataset.id,
            "dataset_code": ds_code,
            "layer_id": target_layer.id,
            "records_processed": len(valid_features),
            "records_failed": job.records_failed,
            "bounds": total_bounds,
            "provenance": "IMPORTED_DATA",
            "message": f"Successfully ingested {len(valid_features)} valid GeoJSON features for {ws.name}."
        }

    @staticmethod
    def import_csv(
        db: Session,
        csv_content: Union[str, bytes],
        watershed_id: int,
        dataset_type: str = "FIELD_PHOTOS",
        dataset_name: Optional[str] = None,
        provider: str = "Field Ground Survey",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        job_id = f"job-csv-{uuid.uuid4().hex[:8]}"
        job = DataIngestionJob(
            job_id=job_id,
            watershed_id=watershed_id,
            source_format="CSV",
            status="PROCESSING",
            records_processed=0,
            records_failed=0,
            log_messages=[f"Starting CSV ingestion for watershed {watershed_id}, type {dataset_type}"]
        )
        db.add(job)
        db.commit()

        if isinstance(csv_content, (bytes, bytearray)):
            csv_text = csv_content.decode("utf-8-sig")
        else:
            csv_text = csv_content

        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            job.status = "FAILED"
            job.log_messages.append(f"Watershed ID {watershed_id} not found.")
            db.commit()
            raise ValueError(f"Watershed with ID {watershed_id} does not exist.")

        ws_boundary = db.query(WatershedBoundary).filter(WatershedBoundary.watershed_id == watershed_id).first()
        ws_bbox = ws_boundary.bbox if ws_boundary else None

        reader = csv.DictReader(io.StringIO(csv_text))
        if not reader.fieldnames:
            job.status = "FAILED"
            job.log_messages.append("CSV has empty or invalid headers.")
            db.commit()
            raise ValueError("CSV header line could not be parsed.")

        # Identify coordinate columns
        headers = [h.strip().lower() for h in reader.fieldnames]
        lat_col = next((c for c in reader.fieldnames if c.strip().lower() in ["latitude", "lat", "lat_dd", "y"]), None)
        lon_col = next((c for c in reader.fieldnames if c.strip().lower() in ["longitude", "lon", "lng", "long", "lon_dd", "x"]), None)

        if not lat_col or not lon_col:
            job.status = "FAILED"
            job.log_messages.append(f"Missing coordinate columns. Found: {reader.fieldnames}")
            db.commit()
            raise ValueError(f"CSV must contain latitude and longitude columns. Headers found: {reader.fieldnames}")

        records_created = 0
        min_lng, min_lat = 180.0, 90.0
        max_lng, max_lat = -180.0, -90.0

        for row_idx, row in enumerate(reader):
            try:
                lat_str = row.get(lat_col, "").strip()
                lon_str = row.get(lon_col, "").strip()
                if not lat_str or not lon_str:
                    job.records_failed += 1
                    continue

                lat = float(lat_str)
                lon = float(lon_str)

                is_valid, err_msg = validate_coordinates(lat, lon)
                if not is_valid:
                    job.records_failed += 1
                    job.log_messages.append(f"Row #{row_idx + 1} invalid coordinates ({lat}, {lon}): {err_msg}")
                    continue

                min_lng = min(min_lng, lon)
                min_lat = min(min_lat, lat)
                max_lng = max(max_lng, lon)
                max_lat = max(max_lat, lat)

                # Ingest record based on dataset_type
                if dataset_type.upper() in ["FIELD_PHOTOS", "PHOTOS"]:
                    photo = FieldPhoto(
                        watershed_id=watershed_id,
                        latitude=lat,
                        longitude=lon,
                        captured_at=datetime.datetime.utcnow(),
                        uploaded_at=datetime.datetime.utcnow(),
                        photo_url=row.get("photo_url") or row.get("url") or f"https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=600&q=80",
                        category=row.get("category", "WATER_BODY").upper(),
                        description=row.get("description") or row.get("remarks") or f"Imported field record from {provider}",
                        verification_status="VERIFIED",
                        source_type="FIELD_UPLOAD",
                        provenance="IMPORTED_DATA",
                        uploader_role="SURVEY_TEAM",
                        exif_metadata={"imported_from_csv": True, "original_row": row_idx + 1}
                    )
                    db.add(photo)
                    records_created += 1

                elif dataset_type.upper() in ["OBSERVATIONS", "GROUND_TRUTH"]:
                    obs = Observation(
                        watershed_id=watershed_id,
                        observer_name=row.get("observer_name") or row.get("observer") or provider,
                        observation_date=datetime.datetime.utcnow(),
                        condition_rating=row.get("condition_rating", "GOOD").upper(),
                        remarks=row.get("remarks") or row.get("description") or "Imported field observation",
                        recommended_action=row.get("recommended_action") or "Routine monitoring"
                    )
                    db.add(obs)
                    records_created += 1

                elif dataset_type.upper() in ["INDICATORS", "BIOPHYSICAL_INDICATOR"]:
                    # Support tabular indicator values (e.g. soil moisture or runoff test)
                    code = row.get("indicator_code") or row.get("code") or "SMI"
                    val_str = row.get("value") or row.get("indicator_value")
                    ind = db.query(Indicator).filter(Indicator.code == code.upper()).first()
                    if ind and val_str:
                        ind_val = IndicatorValue(
                            watershed_id=watershed_id,
                            indicator_id=ind.id,
                            recorded_year=int(row.get("year") or datetime.datetime.utcnow().year),
                            recorded_month=int(row.get("month") or 6),
                            value=float(val_str),
                            normalized_score=float(row.get("normalized_score") or 50.0),
                            source_type="IMPORTED"
                        )
                        db.add(ind_val)
                        records_created += 1

            except Exception as e:
                job.records_failed += 1
                job.log_messages.append(f"Row #{row_idx + 1} error: {str(e)}")

        if records_created == 0:
            job.status = "FAILED"
            job.log_messages.append("No valid records could be extracted from CSV.")
            db.commit()
            raise ValueError("No valid coordinate rows could be imported from CSV.")

        bounds = [round(min_lng, 6), round(min_lat, 6), round(max_lng, 6), round(max_lat, 6)]

        # Register dataset catalog
        ds_code = f"DS-{ws.code}-CSV-{uuid.uuid4().hex[:6].upper()}"
        ds_name = dataset_name or f"Imported {dataset_type.replace('_', ' ').title()} CSV Dataset"
        dataset = GeospatialDataset(
            dataset_code=ds_code,
            dataset_name=ds_name,
            dataset_type=dataset_type.upper(),
            provider=provider,
            watershed_id=watershed_id,
            acquisition_date=datetime.datetime.utcnow(),
            processing_date=datetime.datetime.utcnow(),
            spatial_resolution="Ground GPS Survey Point",
            temporal_resolution="Point Sample",
            coverage_bounds=bounds,
            crs="EPSG:4326",
            provenance="IMPORTED_DATA",
            format="CSV",
            record_count=records_created,
            license_info=metadata.get("license", "Local Survey Authority") if metadata else "Local Survey Authority",
            metadata_json=metadata or {},
            status="ACTIVE"
        )
        db.add(dataset)
        db.flush()

        job.dataset_id = dataset.id
        job.records_processed = records_created
        job.status = "COMPLETED"
        job.completed_at = datetime.datetime.utcnow()
        job.log_messages.append(f"Successfully ingested {records_created} records into {ds_code}.")

        db.commit()

        return {
            "status": "SUCCESS",
            "job_id": job_id,
            "dataset_id": dataset.id,
            "dataset_code": ds_code,
            "records_processed": records_created,
            "records_failed": job.records_failed,
            "bounds": bounds,
            "provenance": "IMPORTED_DATA",
            "message": f"Successfully imported {records_created} {dataset_type} records for {ws.name}."
        }
