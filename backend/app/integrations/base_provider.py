"""
JalDrishti AI — Abstract Satellite Data Provider Interface
Standardizes multi-constellation Earth Observation (EO) scene discovery,
spectral band acquisition, and cloud-masking workflows across providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import datetime

@dataclass
class SatelliteSceneMetadata:
    scene_id: str
    provider: str # Copernicus CDSE, USGS Landsat, NRSC Bhuvan
    satellite_name: str # Sentinel-2A/B, Landsat 8/9, Resourcesat-2
    acquisition_time: datetime.datetime
    cloud_cover_pct: float
    footprint_bbox: List[float] # [min_lng, min_lat, max_lng, max_lat]
    spatial_resolution_m: float
    available_bands: List[str] = field(default_factory=list)
    product_type: str = "L2A_BOA_REFLECTANCE"
    download_url: Optional[str] = None
    is_preview_available: bool = False

class BaseSatelliteProvider(ABC):
    """
    Provider-agnostic interface for future satellite imagery streams.
    Workflow: area/watershed -> dataset selection -> acquisition -> preprocessing -> feature extraction.
    """

    @property
    @abstractmethod
    def provider_code(self) -> str:
        """Unique identifier code for the provider."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider label."""
        pass

    @property
    @abstractmethod
    def default_resolution_m(self) -> float:
        """Nominal ground sampling distance in meters."""
        pass

    @abstractmethod
    def get_configuration_status(self) -> Dict[str, Any]:
        """
        Returns the operational connection status and configuration parameter report.
        Clearly indicates if production government/enterprise credentials are required.
        """
        pass

    @abstractmethod
    def search_scenes(
        self,
        bbox: List[float],
        start_date: datetime.date,
        end_date: datetime.date,
        max_cloud_cover_pct: float = 20.0
    ) -> List[SatelliteSceneMetadata]:
        """
        Searches the provider catalog for satellite scenes covering the specified bounding box.
        """
        pass
