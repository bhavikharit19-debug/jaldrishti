"""
JalDrishti AI — Earth Observation & Geospatial Provider Registry
Registers, manages, and reports connection status for authoritative satellite/GIS adapters.
"""

from typing import Dict, Any, List
from app.integrations.copernicus_adapter import Sentinel2CopernicusAdapter
from app.integrations.bhuvan_adapter import BhuvanISROAdapter
from app.integrations.landsat_adapter import LandsatUSGSAdapter

class ProviderRegistry:
    _adapters = {
        "COPERNICUS_SENTINEL2": Sentinel2CopernicusAdapter(),
        "NRSC_BHUVAN": BhuvanISROAdapter(),
        "USGS_LANDSAT": LandsatUSGSAdapter()
    }

    @classmethod
    def list_adapters(cls) -> List[Dict[str, Any]]:
        """Returns configuration status and capabilities for all registered adapters."""
        return [adapter.get_configuration_status() for adapter in cls._adapters.values()]

    @classmethod
    def get_adapter(cls, provider_code: str):
        """Retrieves an adapter by its provider code."""
        return cls._adapters.get(provider_code.upper())
