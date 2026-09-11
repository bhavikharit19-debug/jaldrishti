"""
JalDrishti AI — Geo-Tagged EXIF Metadata Extraction Engine
Extracts GPS coordinates, altitude, orientation, capture timestamp, and device metadata
from raw field photograph byte payloads using Pillow.
"""

import io
import datetime
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags

class ExifExtractor:
    @staticmethod
    def _convert_to_degrees(value) -> float:
        """
        Converts GPS DMS (degrees, minutes, seconds) tuple/rational to decimal degrees.
        Handles IFDRational objects and float/int tuples.
        """
        try:
            # Handle list or tuple of (deg, min, sec)
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)
        except Exception:
            return float(value)

    @classmethod
    def extract_from_bytes(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Parses raw image bytes and extracts geo-tagged GPS and camera metadata.
        Returns a standardized dictionary.
        """
        result = {
            "has_gps": False,
            "latitude": None,
            "longitude": None,
            "altitude_m": None,
            "captured_at": None,
            "device_make": None,
            "device_model": None,
            "image_dimensions": None,
            "raw_metadata": {}
        }

        if not image_bytes:
            return result

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                result["image_dimensions"] = {"width": img.width, "height": img.height, "format": img.format}
                
                exif_data = img._getexif() if hasattr(img, "_getexif") else None
                if not exif_data:
                    return result

                labeled_exif = {}
                gps_info = {}

                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag_name == "GPSInfo":
                        for t in value:
                            sub_tag = ExifTags.GPSTAGS.get(t, t)
                            gps_info[sub_tag] = value[t]
                    else:
                        # Clean serializable values
                        if isinstance(value, (bytes, bytearray)):
                            continue
                        labeled_exif[str(tag_name)] = str(value)

                # Device and timestamp extraction
                result["device_make"] = labeled_exif.get("Make")
                result["device_model"] = labeled_exif.get("Model")
                
                raw_time = labeled_exif.get("DateTimeOriginal") or labeled_exif.get("DateTime")
                if raw_time:
                    try:
                        # Standard EXIF format: 'YYYY:MM:DD HH:MM:SS'
                        dt = datetime.datetime.strptime(raw_time, "%Y:%m:%d %H:%M:%S")
                        result["captured_at"] = dt.isoformat()
                    except Exception:
                        result["captured_at"] = raw_time

                # GPS extraction
                if gps_info:
                    lat_val = gps_info.get("GPSLatitude")
                    lat_ref = gps_info.get("GPSLatitudeRef")
                    lon_val = gps_info.get("GPSLongitude")
                    lon_ref = gps_info.get("GPSLongitudeRef")

                    if lat_val and lon_val:
                        lat = cls._convert_to_degrees(lat_val)
                        if lat_ref == "S":
                            lat = -lat

                        lon = cls._convert_to_degrees(lon_val)
                        if lon_ref == "W":
                            lon = -lon

                        result["latitude"] = round(lat, 6)
                        result["longitude"] = round(lon, 6)
                        result["has_gps"] = True

                    alt_val = gps_info.get("GPSAltitude")
                    if alt_val is not None:
                        try:
                            result["altitude_m"] = round(float(alt_val), 1)
                        except Exception:
                            pass

                result["raw_metadata"] = {k: v for k, v in labeled_exif.items() if len(str(v)) < 150}

        except Exception as e:
            result["error"] = str(e)

        return result
