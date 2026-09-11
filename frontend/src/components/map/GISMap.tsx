'use client';
import React, { useEffect, useRef, useState } from 'react';
import { WatershedDetail, GISLayer, FieldPhoto, InterventionItem } from '@/types';
import { LayerControl, LayerVisibility } from './LayerControl';
import { MapLegend } from './MapLegend';
import { PhotoPopup } from './PhotoPopup';
import { FeaturePopup, FeaturePopupData } from './FeaturePopup';
import { createRoot } from 'react-dom/client';
import { Maximize2, Minimize2, Navigation, Compass, Layers, Globe } from 'lucide-react';

const VECTOR_STYLE = {
  version: 8,
  sources: {
    'osm-tiles': {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '&copy; OpenStreetMap contributors'
    }
  },
  layers: [
    {
      id: 'osm-tiles-layer',
      type: 'raster',
      source: 'osm-tiles',
      minzoom: 0,
      maxzoom: 19
    }
  ]
};

const SATELLITE_STYLE = {
  version: 8,
  sources: {
    'satellite-tiles': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
      ],
      tileSize: 256,
      attribution: 'Esri, Maxar, Earthstar Geographics'
    }
  },
  layers: [
    {
      id: 'satellite-tiles-layer',
      type: 'raster',
      source: 'satellite-tiles',
      minzoom: 0,
      maxzoom: 19
    }
  ]
};

interface GISMapProps {
  watershed?: WatershedDetail;
  layers?: GISLayer[];
  photos?: FieldPhoto[];
  interventions?: InterventionItem[];
  className?: string;
  controlledVisibility?: LayerVisibility;
  onVisibilityChange?: (key: keyof LayerVisibility, val: boolean) => void;
  showFloatingLayerControl?: boolean;
}

export const GISMap: React.FC<GISMapProps> = ({
  watershed,
  layers = [],
  photos = [],
  interventions = [],
  className = 'h-[580px]',
  controlledVisibility,
  onVisibilityChange,
  showFloatingLayerControl = true
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const activePopupRef = useRef<any>(null);

  const [internalVisibility, setInternalVisibility] = useState<LayerVisibility>({
    boundary: true,
    satellite: false,
    drainage: true,
    waterBodies: true,
    lulc: true,
    vegetation: false,
    elevation: false,
    interventions: true,
    fieldPhotos: true
  });

  const visibility = controlledVisibility || internalVisibility;

  const [showLegend, setShowLegend] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleVisibilityChange = (key: keyof LayerVisibility, val: boolean) => {
    if (onVisibilityChange) {
      onVisibilityChange(key, val);
    } else {
      setInternalVisibility((prev) => ({ ...prev, [key]: val }));
    }
  };

  // 1. Initialize MapLibre
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    let mapInstance: any;

    const initMap = async () => {
      const maplibregl = (await import('maplibre-gl')).default;

      const defaultCenter: [number, number] = watershed?.boundary
        ? [watershed.boundary.centroid_lng, watershed.boundary.centroid_lat]
        : [74.605, 19.048];

      mapInstance = new maplibregl.Map({
        container: mapContainer.current!,
        style: visibility.satellite ? (SATELLITE_STYLE as any) : (VECTOR_STYLE as any),
        center: defaultCenter,
        zoom: 13,
      });

      mapInstance.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-left');
      mapInstance.addControl(new maplibregl.ScaleControl({ maxWidth: 100, unit: 'metric' }), 'bottom-left');

      mapRef.current = mapInstance;

      mapInstance.on('load', () => {
        updateMapLayers(mapInstance);
      });
    };

    initMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // 2. Update Basemap Style
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;
    const style = visibility.satellite ? SATELLITE_STYLE : VECTOR_STYLE;

    map.setStyle(style as any);
    map.once('style.load', () => {
      updateMapLayers(map);
    });
  }, [visibility.satellite]);

  // 3. Update Layers
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;
    updateMapLayers(mapRef.current);
  }, [watershed, layers, interventions, visibility]);

  // 4. Update Photo Markers
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    if (!visibility.fieldPhotos) return;

    import('maplibre-gl').then(({ default: maplibregl }) => {
      photos.forEach((photo) => {
        const el = document.createElement('div');
        el.className =
          'h-7 w-7 rounded-full bg-purple-600 border-2 border-white shadow-md flex items-center justify-center cursor-pointer hover:scale-110 transition-transform';
        el.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
            <circle cx="12" cy="13" r="3"/>
          </svg>
        `;

        const popupContainer = document.createElement('div');
        const root = createRoot(popupContainer);
        root.render(<PhotoPopup photo={photo} />);

        const popup = new maplibregl.Popup({ offset: 25, closeButton: false }).setDOMContent(
          popupContainer
        );

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([photo.longitude, photo.latitude])
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      });
    });
  }, [photos, visibility.fieldPhotos]);

  // 5. Fit to Bounds on Watershed Change
  const fitToBoundary = () => {
    if (!mapRef.current || !watershed?.boundary?.bbox) return;
    const [minLng, minLat, maxLng, maxLat] = watershed.boundary.bbox;
    mapRef.current.fitBounds(
      [
        [minLng, minLat],
        [maxLng, maxLat],
      ],
      { padding: 50, duration: 1200 }
    );
  };

  useEffect(() => {
    fitToBoundary();
  }, [watershed]);

  // 6. Setup Interactive Click Popups on Vector Features
  const setupFeatureClickListeners = (map: any, layerId: string, layerType: FeaturePopupData['layerType']) => {
    import('maplibre-gl').then(({ default: maplibregl }) => {
      map.off('click', layerId);
      map.on('click', layerId, (e: any) => {
        if (!e.features || e.features.length === 0) return;
        const feature = e.features[0];

        if (activePopupRef.current) {
          activePopupRef.current.remove();
        }

        const popupContainer = document.createElement('div');
        const root = createRoot(popupContainer);
        root.render(
          <FeaturePopup
            data={{
              layerType,
              properties: feature.properties,
            }}
          />
        );

        const popup = new maplibregl.Popup({ offset: 12, closeButton: false })
          .setLngLat(e.lngLat)
          .setDOMContent(popupContainer)
          .addTo(map);

        activePopupRef.current = popup;
      });

      // Hover cursor style
      map.on('mouseenter', layerId, () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', layerId, () => {
        map.getCanvas().style.cursor = '';
      });
    });
  };

  const updateMapLayers = (map: any) => {
    if (!map || !map.isStyleLoaded()) return;

    // 1. Boundary
    if (watershed?.boundary?.geometry) {
      if (!map.getSource('watershed-boundary-src')) {
        map.addSource('watershed-boundary-src', {
          type: 'geojson',
          data: {
            type: 'Feature',
            geometry: watershed.boundary.geometry,
            properties: {},
          },
        });

        map.addLayer({
          id: 'watershed-boundary-fill',
          type: 'fill',
          source: 'watershed-boundary-src',
          paint: {
            'fill-color': '#2563eb',
            'fill-opacity': 0.06,
          },
        });

        map.addLayer({
          id: 'watershed-boundary-line',
          type: 'line',
          source: 'watershed-boundary-src',
          paint: {
            'line-color': '#1d4ed8',
            'line-width': 2.5,
            'line-dasharray': [2, 1],
          },
        });
      } else {
        map.getSource('watershed-boundary-src').setData({
          type: 'Feature',
          geometry: watershed.boundary.geometry,
          properties: {},
        });
      }

      if (map.getLayer('watershed-boundary-fill')) {
        map.setLayoutProperty('watershed-boundary-fill', 'visibility', visibility.boundary ? 'visible' : 'none');
      }
      if (map.getLayer('watershed-boundary-line')) {
        map.setLayoutProperty('watershed-boundary-line', 'visibility', visibility.boundary ? 'visible' : 'none');
      }
    }

    // 2. Thematic Vector Layers
    layers.forEach((layer) => {
      const srcId = `gis-layer-src-${layer.id}`;
      const fillId = `gis-layer-fill-${layer.id}`;
      const lineId = `gis-layer-line-${layer.id}`;

      if (layer.data_payload) {
        if (!map.getSource(srcId)) {
          map.addSource(srcId, {
            type: 'geojson',
            data: layer.data_payload,
          });

          if (layer.layer_type === 'DRAINAGE') {
            map.addLayer({
              id: lineId,
              type: 'line',
              source: srcId,
              paint: {
                'line-color': '#0284c7',
                'line-width': ['interpolate', ['linear'], ['get', 'order'], 1, 1.8, 2, 2.8, 3, 4.5],
              },
            });
            setupFeatureClickListeners(map, lineId, 'DRAINAGE');
          } else if (layer.layer_type === 'WATER_BODIES') {
            map.addLayer({
              id: fillId,
              type: 'fill',
              source: srcId,
              paint: {
                'fill-color': '#00bcd4',
                'fill-opacity': 0.7,
              },
            });
            map.addLayer({
              id: lineId,
              type: 'line',
              source: srcId,
              paint: {
                'line-color': '#0097a7',
                'line-width': 1.8,
              },
            });
            setupFeatureClickListeners(map, fillId, 'WATER_BODIES');
          } else if (layer.layer_type === 'LULC') {
            map.addLayer({
              id: fillId,
              type: 'fill',
              source: srcId,
              paint: {
                'fill-color': ['get', 'color'],
                'fill-opacity': 0.35,
              },
            });
            map.addLayer({
              id: lineId,
              type: 'line',
              source: srcId,
              paint: {
                'line-color': ['get', 'color'],
                'line-width': 1,
                'line-opacity': 0.7,
              },
            });
            setupFeatureClickListeners(map, fillId, 'LULC');
          } else if (layer.layer_type === 'VEGETATION_NDVI') {
            map.addLayer({
              id: fillId,
              type: 'fill',
              source: srcId,
              paint: {
                'fill-color': ['get', 'color'],
                'fill-opacity': 0.38,
              },
            });
            map.addLayer({
              id: lineId,
              type: 'line',
              source: srcId,
              paint: {
                'line-color': ['get', 'color'],
                'line-width': 1,
                'line-opacity': 0.6,
              },
            });
            setupFeatureClickListeners(map, fillId, 'VEGETATION_NDVI');
          } else if (layer.layer_type === 'ELEVATION') {
            map.addLayer({
              id: fillId,
              type: 'fill',
              source: srcId,
              paint: {
                'fill-color': ['get', 'color'],
                'fill-opacity': 0.35,
              },
            });
            map.addLayer({
              id: lineId,
              type: 'line',
              source: srcId,
              paint: {
                'line-color': '#5d4037',
                'line-width': 1.2,
                'line-opacity': 0.8,
              },
            });
            setupFeatureClickListeners(map, fillId, 'ELEVATION');
          }
        }

        // Toggle Layer Visibility
        const isVisible =
          (layer.layer_type === 'DRAINAGE' && visibility.drainage) ||
          (layer.layer_type === 'WATER_BODIES' && visibility.waterBodies) ||
          (layer.layer_type === 'LULC' && visibility.lulc) ||
          (layer.layer_type === 'VEGETATION_NDVI' && visibility.vegetation) ||
          (layer.layer_type === 'ELEVATION' && visibility.elevation);

        if (map.getLayer(fillId)) {
          map.setLayoutProperty(fillId, 'visibility', isVisible ? 'visible' : 'none');
        }
        if (map.getLayer(lineId)) {
          map.setLayoutProperty(lineId, 'visibility', isVisible ? 'visible' : 'none');
        }
      }
    });

    // 3. Interventions Layer
    if (interventions.length > 0) {
      const intFeatures = interventions.map((i) => ({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [i.longitude, i.latitude],
        },
        properties: {
          name: i.name,
          type: i.intervention_type.replace(/_/g, ' '),
          status: i.status,
          beneficiaries: i.beneficiary_count,
        },
      }));

      if (!map.getSource('interventions-src')) {
        map.addSource('interventions-src', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: intFeatures,
          },
        });

        map.addLayer({
          id: 'interventions-circle',
          type: 'circle',
          source: 'interventions-src',
          paint: {
            'circle-radius': 7.5,
            'circle-color': '#ea580c',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
          },
        });

        setupFeatureClickListeners(map, 'interventions-circle', 'INTERVENTIONS');
      } else {
        map.getSource('interventions-src').setData({
          type: 'FeatureCollection',
          features: intFeatures,
        });
      }

      if (map.getLayer('interventions-circle')) {
        map.setLayoutProperty(
          'interventions-circle',
          'visibility',
          visibility.interventions ? 'visible' : 'none'
        );
      }
    }
  };

  const drainageCount = layers.find((l) => l.layer_type === 'DRAINAGE')?.data_payload?.features?.length;
  const waterBodiesCount = layers.find((l) => l.layer_type === 'WATER_BODIES')?.data_payload?.features?.length;
  const lulcCount = layers.find((l) => l.layer_type === 'LULC')?.data_payload?.features?.length;

  return (
    <div
      className={`relative w-full rounded-xl overflow-hidden border border-slate-200 shadow-sm ${
        isFullscreen ? 'fixed inset-0 z-50 h-screen rounded-none' : className
      }`}
    >
      <div ref={mapContainer} className="h-full w-full" />

      {/* Floating Map Tools */}
      <div className="absolute top-4 left-14 z-20 flex items-center space-x-1.5 bg-white/90 backdrop-blur-sm p-1 rounded-lg border border-slate-200 shadow-md">
        <button
          type="button"
          onClick={fitToBoundary}
          title="Zoom to Watershed Boundary"
          className="p-1.5 text-slate-600 hover:text-blue-700 hover:bg-slate-100 rounded transition-colors flex items-center space-x-1 text-xs font-semibold"
        >
          <Compass className="h-3.5 w-3.5 text-blue-600" />
          <span className="hidden sm:inline">Fit Bounds</span>
        </button>

        <button
          type="button"
          onClick={() => setIsFullscreen(!isFullscreen)}
          title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          className="p-1.5 text-slate-600 hover:text-blue-700 hover:bg-slate-100 rounded transition-colors"
        >
          {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Selected Watershed Badge */}
      {watershed && (
        <div className="absolute top-4 left-44 sm:left-48 z-10 hidden md:flex items-center space-x-2 bg-slate-900/85 backdrop-blur-md text-white px-3 py-1.5 rounded-lg text-xs shadow-md border border-slate-700">
          <Globe className="h-3.5 w-3.5 text-blue-400" />
          <span className="font-bold">{watershed.name}</span>
          <span className="text-slate-400 text-[10px]">({watershed.area_hectares} ha)</span>
        </div>
      )}

      {/* Interactive Layer Switcher */}
      {showFloatingLayerControl && (
        <LayerControl
          visibility={visibility}
          onChange={handleVisibilityChange}
          counts={{
            drainageFeatures: drainageCount,
            waterBodies: waterBodiesCount,
            interventions: interventions.length,
            photos: photos.length,
            lulcClasses: lulcCount,
          }}
          showLegend={showLegend}
          onToggleLegend={() => setShowLegend(!showLegend)}
        />
      )}

      {/* Collapsible Thematic Map Legend */}
      <MapLegend
        visibility={visibility}
        isOpen={showLegend}
        onClose={() => setShowLegend(false)}
      />
    </div>
  );
};
