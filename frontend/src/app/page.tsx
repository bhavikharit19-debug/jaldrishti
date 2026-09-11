'use client';
import React, { useEffect, useState } from 'react';
import {
  StateHierarchy,
  WatershedListItem,
  WatershedDetail,
  GISLayer,
  FieldPhoto,
  HealthScore,
  InterventionItem,
  AlertItem,
  WatershedGISStats
} from '@/types';
import { api } from '@/services/api';
import { Header } from '@/components/dashboard/Header';
import { SidebarNav } from '@/components/dashboard/SidebarNav';
import { WatershedSelector } from '@/components/dashboard/WatershedSelector';
import GISControlPanel from '@/components/dashboard/GISControlPanel';
import CatchmentInspector from '@/components/dashboard/CatchmentInspector';
import { GISMap } from '@/components/map/GISMap';
import { LayerVisibility } from '@/components/map/LayerControl';
import { IndicatorsPanel } from '@/components/dashboard/IndicatorsPanel';
import { ChangeDetectionPanel } from '@/components/dashboard/ChangeDetectionPanel';
import { PredictionsPanel } from '@/components/dashboard/PredictionsPanel';
import { RiskAssessmentPanel } from '@/components/dashboard/RiskAssessmentPanel';
import { RecommendationsPanel } from '@/components/dashboard/RecommendationsPanel';
import { InterventionsPanel } from '@/components/dashboard/InterventionsPanel';
import { AlertsPanel } from '@/components/dashboard/AlertsPanel';
import { FieldPhotosModal } from '@/components/dashboard/FieldPhotosModal';
import { DataIntegrationModal } from '@/components/dashboard/DataIntegrationModal';
import { AdminModal } from '@/components/dashboard/AdminModal';
import { useAuth } from '@/context/AuthContext';
import {
  Map as MapIcon,
  Layers,
  Activity,
  History,
  Cpu,
  ShieldAlert,
  Hammer,
  Camera,
  ChevronDown,
  ChevronUp,
  PanelRightClose,
  PanelRightOpen,
  Maximize2
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  // Master Catchment State
  const [states, setStates] = useState<StateHierarchy[]>([]);
  const [watersheds, setWatersheds] = useState<WatershedListItem[]>([]);
  const [selectedWatershedId, setSelectedWatershedId] = useState<number>(1);
  const [currentWatershed, setCurrentWatershed] = useState<WatershedDetail | undefined>();
  const [layers, setLayers] = useState<GISLayer[]>([]);
  const [photos, setPhotos] = useState<FieldPhoto[]>([]);
  const [healthScore, setHealthScore] = useState<HealthScore | undefined>();
  const [interventions, setInterventions] = useState<InterventionItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [gisStats, setGisStats] = useState<WatershedGISStats | undefined>();

  // Layer Visibility State (Shared between Left GIS Control Panel and MapLibre Map)
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
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

  const handleLayerToggle = (key: keyof LayerVisibility, val: boolean) => {
    setLayerVisibility((prev) => ({ ...prev, [key]: val }));
  };

  // UI state
  const [activeTab, setActiveTab] = useState<string>('gis_intelligence');
  const [showRightInspector, setShowRightInspector] = useState(true);
  const [showBottomDrawer, setShowBottomDrawer] = useState(false);
  const [bottomDrawerTab, setBottomDrawerTab] = useState<
    'predictions' | 'risks' | 'recommendations' | 'interventions' | 'indicators'
  >('predictions');

  const [isPhotoModalOpen, setIsPhotoModalOpen] = useState(false);
  const [isDataModalOpen, setIsDataModalOpen] = useState(false);
  const [isAdminModalOpen, setIsAdminModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const { user } = useAuth();

  // 1. Initial Load: States hierarchy and watersheds list
  useEffect(() => {
    Promise.all([
      api.getStatesHierarchy().catch(() => []),
      api.listWatersheds().catch(() => [])
    ]).then(([statesRes, wsRes]) => {
      setStates(statesRes);
      setWatersheds(wsRes);
      if (wsRes.length > 0) {
        const defaultId = user?.watershed_id || wsRes[0].id;
        setSelectedWatershedId(defaultId);
      }
      setLoading(false);
    });
  }, [user]);

  // 2. Load watershed dependent data
  const loadWatershedData = (id: number) => {
    api.getWatershed(id)
      .then(setCurrentWatershed)
      .catch((err) => console.error('Failed to get watershed:', err));

    api.getLayers(id)
      .then(setLayers)
      .catch((err) => console.error('Failed to get layers:', err));

    api.getWatershedGISStats(id)
      .then(setGisStats)
      .catch((err) => console.error('Failed to get GIS stats:', err));

    api.getPhotos(id)
      .then(setPhotos)
      .catch((err) => console.error('Failed to get photos:', err));

    api.getHealthScore(id)
      .then(setHealthScore)
      .catch((err) => console.error('Failed to get health score:', err));

    api.getInterventions(id)
      .then(setInterventions)
      .catch((err) => console.error('Failed to get interventions:', err));

    api.getAlerts(id)
      .then(setAlerts)
      .catch((err) => console.error('Failed to get alerts:', err));
  };

  useEffect(() => {
    if (selectedWatershedId) {
      loadWatershedData(selectedWatershedId);
    }
  }, [selectedWatershedId]);

  // Handle cascading filter
  const handleFilterChange = (stateId?: number, districtId?: number, search?: string) => {
    api.listWatersheds(stateId, districtId, search).then((res) => {
      setWatersheds(res);
      if (res.length > 0 && !res.some((w) => w.id === selectedWatershedId)) {
        setSelectedWatershedId(res[0].id);
      }
    });
  };

  const activeAlertsCount = alerts.filter((a) => a.status === 'ACTIVE').length;

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-800">
      {/* 1. JalDrishti Header */}
      <Header
        watershedName={currentWatershed?.name}
        alertsCount={activeAlertsCount}
        onOpenAlerts={() => setActiveTab('alerts')}
        selectedWatershedId={selectedWatershedId}
        onOpenDataIntegration={() => setIsDataModalOpen(true)}
        onOpenAdminModal={() => setIsAdminModalOpen(true)}
      />

      {/* 2. Sub-Navigation Bar */}
      <SidebarNav
        activeSection={activeTab}
        onSelectSection={(sec) => setActiveTab(sec)}
        onOpenAdminModal={() => setIsAdminModalOpen(true)}
        onOpenDataModal={() => setIsDataModalOpen(true)}
        onOpenPhotoModal={() => setIsPhotoModalOpen(true)}
        selectedWatershedId={selectedWatershedId}
      />

      {/* 3. Administrative Hierarchy Breadcrumb Filter */}
      <WatershedSelector
        states={states}
        watersheds={watersheds}
        selectedWatershedId={selectedWatershedId}
        onSelectWatershed={(id) => setSelectedWatershedId(id)}
        onFilterChange={handleFilterChange}
        currentWatershed={currentWatershed}
        healthScore={healthScore}
      />

      {/* 4. Main Workstation Body */}
      {activeTab === 'gis_intelligence' ? (
        /* MAP-FIRST GIS WORKSTATION LAYOUT */
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 flex overflow-hidden relative">
            {/* LEFT: GIS Layer & Hierarchy Control Panel */}
            <div className="hidden md:block flex-shrink-0">
              <GISControlPanel
                watershed={currentWatershed}
                states={states}
                watersheds={watersheds}
                selectedWatershedId={selectedWatershedId}
                onSelectWatershed={(id) => setSelectedWatershedId(id)}
                onFilterChange={handleFilterChange}
                layerVisibility={layerVisibility}
                onLayerToggle={handleLayerToggle}
                onSelectTab={(tab) => {
                  if (['change', 'predictions', 'risks', 'recommendations', 'interventions'].includes(tab)) {
                    setActiveTab(tab);
                  }
                }}
                onOpenReport={() => {
                  window.location.href = `/reports?id=${selectedWatershedId}`;
                }}
                onOpenDataCatalog={() => setIsDataModalOpen(true)}
                onOpenPhotoModal={() => setIsPhotoModalOpen(true)}
              />
            </div>

            {/* CENTER: Large Interactive GIS Map */}
            <div className="flex-1 flex flex-col relative h-[640px] md:h-[calc(100vh-190px)] min-w-0 bg-slate-900">
              <GISMap
                watershed={currentWatershed}
                layers={layers}
                photos={photos}
                interventions={interventions}
                className="h-full w-full rounded-none"
                controlledVisibility={layerVisibility}
                onVisibilityChange={handleLayerToggle}
                showFloatingLayerControl={false}
              />

              {/* Inspector Toggle Button on Right Map Edge */}
              <button
                type="button"
                onClick={() => setShowRightInspector(!showRightInspector)}
                className="absolute top-4 right-4 z-20 p-2 bg-white/95 hover:bg-white text-slate-800 border border-slate-300 rounded shadow-md text-xs font-bold flex items-center space-x-1"
                title={showRightInspector ? 'Hide Catchment Inspector' : 'Show Catchment Inspector'}
              >
                {showRightInspector ? (
                  <>
                    <PanelRightClose className="h-4 w-4 text-blue-900" />
                    <span className="hidden sm:inline">Hide Profile</span>
                  </>
                ) : (
                  <>
                    <PanelRightOpen className="h-4 w-4 text-blue-900" />
                    <span className="hidden sm:inline">Inspect Catchment</span>
                  </>
                )}
              </button>

              {/* Bottom Analysis Drawer Trigger Bar */}
              <div className="absolute bottom-0 left-0 right-0 z-20 bg-slate-900/90 backdrop-blur-xs border-t border-slate-700 text-white px-4 py-1.5 flex items-center justify-between text-xs">
                <div className="flex items-center space-x-3">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider hidden sm:inline">
                    Catchment Analysis Drawer:
                  </span>
                  <div className="flex items-center space-x-1">
                    <button
                      type="button"
                      onClick={() => {
                        setBottomDrawerTab('predictions');
                        setShowBottomDrawer(true);
                      }}
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        showBottomDrawer && bottomDrawerTab === 'predictions'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Predictions
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setBottomDrawerTab('risks');
                        setShowBottomDrawer(true);
                      }}
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        showBottomDrawer && bottomDrawerTab === 'risks'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Risk Matrix
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setBottomDrawerTab('recommendations');
                        setShowBottomDrawer(true);
                      }}
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        showBottomDrawer && bottomDrawerTab === 'recommendations'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Decision Support
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setBottomDrawerTab('interventions');
                        setShowBottomDrawer(true);
                      }}
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        showBottomDrawer && bottomDrawerTab === 'interventions'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Interventions
                    </button>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setShowBottomDrawer(!showBottomDrawer)}
                  className="text-slate-300 hover:text-white flex items-center space-x-1 text-[11px] font-semibold"
                >
                  <span>{showBottomDrawer ? 'Minimize Table' : 'Expand Data Table'}</span>
                  {showBottomDrawer ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                </button>
              </div>

              {/* Expandable Bottom Drawer */}
              {showBottomDrawer && (
                <div className="absolute bottom-9 left-0 right-0 z-30 max-h-72 overflow-y-auto bg-white border-t-2 border-blue-900 shadow-2xl p-4">
                  {bottomDrawerTab === 'predictions' && (
                    <PredictionsPanel watershedId={selectedWatershedId} />
                  )}
                  {bottomDrawerTab === 'risks' && (
                    <RiskAssessmentPanel watershedId={selectedWatershedId} />
                  )}
                  {bottomDrawerTab === 'recommendations' && (
                    <RecommendationsPanel watershedId={selectedWatershedId} />
                  )}
                  {bottomDrawerTab === 'interventions' && (
                    <InterventionsPanel watershedId={selectedWatershedId} />
                  )}
                </div>
              )}
            </div>

            {/* RIGHT: Catchment Profile Inspector */}
            {showRightInspector && (
              <div className="hidden lg:block flex-shrink-0">
                <CatchmentInspector
                  watershed={currentWatershed}
                  healthScore={healthScore}
                  alerts={alerts}
                  interventions={interventions}
                  photos={photos}
                  onOpenReport={() => {
                    window.location.href = `/reports?id=${selectedWatershedId}`;
                  }}
                  onOpenPhotoModal={() => setIsPhotoModalOpen(true)}
                  onSelectTab={(tab) => setActiveTab(tab)}
                  onClose={() => setShowRightInspector(false)}
                />
              </div>
            )}
          </div>
        </div>
      ) : (
        /* DEDICATED FULL ANALYTICAL MODULE VIEW */
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-4">
          <div className="flex items-center justify-between bg-white px-4 py-2 rounded border border-slate-300">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Active Module:
              </span>
              <span className="text-xs font-bold text-blue-950 uppercase font-mono">
                {activeTab.replace(/_/g, ' ')}
              </span>
            </div>
            <button
              type="button"
              onClick={() => setActiveTab('gis_intelligence')}
              className="px-3 py-1 bg-blue-900 hover:bg-blue-950 text-white rounded text-xs font-bold flex items-center space-x-1"
            >
              <MapIcon className="h-3.5 w-3.5" />
              <span>Return to GIS Map Workstation</span>
            </button>
          </div>

          {activeTab === 'indicators' && (
            <IndicatorsPanel healthScore={healthScore} />
          )}

          {activeTab === 'change' && (
            <ChangeDetectionPanel watershedId={selectedWatershedId} />
          )}

          {activeTab === 'predictions' && (
            <PredictionsPanel watershedId={selectedWatershedId} />
          )}

          {activeTab === 'risks' && (
            <RiskAssessmentPanel watershedId={selectedWatershedId} />
          )}

          {activeTab === 'recommendations' && (
            <RecommendationsPanel watershedId={selectedWatershedId} />
          )}

          {activeTab === 'interventions' && (
            <InterventionsPanel watershedId={selectedWatershedId} />
          )}

          {activeTab === 'alerts' && (
            <AlertsPanel
              watershedId={selectedWatershedId}
              onAlertUpdated={() => loadWatershedData(selectedWatershedId)}
            />
          )}
        </main>
      )}

      {/* Modals */}
      <FieldPhotosModal
        watershedId={selectedWatershedId}
        photos={photos}
        isOpen={isPhotoModalOpen}
        onClose={() => setIsPhotoModalOpen(false)}
        onPhotoUploaded={() => loadWatershedData(selectedWatershedId)}
      />

      <DataIntegrationModal
        watershedId={selectedWatershedId}
        watershedName={currentWatershed?.name || 'Catchment'}
        isOpen={isDataModalOpen}
        onClose={() => setIsDataModalOpen(false)}
        onImportSuccess={() => loadWatershedData(selectedWatershedId)}
      />

      <AdminModal
        isOpen={isAdminModalOpen}
        onClose={() => setIsAdminModalOpen(false)}
      />
    </div>
  );
}
