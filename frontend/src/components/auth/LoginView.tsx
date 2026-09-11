'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { api, getApiBaseUrl } from '@/services/api';
import {
  Shield,
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
  Building,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Info,
  KeyRound,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Layers,
  MapPin,
  Check,
  X
} from 'lucide-react';
import Link from 'next/link';
import JalDrishtiLogo from '@/components/common/JalDrishtiLogo';
import { RegistrationResponse, ForgotPasswordResponse } from '@/types';

type AuthMode = 'login' | 'register' | 'forgot' | 'request_access';

export default function LoginView({ initialTab = 'login' }: { initialTab?: AuthMode }) {
  const router = useRouter();
  const { login, quickDemoLogin, demoAccounts, isAuthenticated } = useAuth();

  const [activeTab, setActiveTab] = useState<AuthMode>(initialTab);

  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Register form state
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regOrg, setRegOrg] = useState('');
  const [regStateId, setRegStateId] = useState<number | ''>(1);
  const [regDistrictId, setRegDistrictId] = useState<number | ''>(1);
  const [regRole, setRegRole] = useState('FIELD_OFFICER');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [regShowPassword, setRegShowPassword] = useState(false);
  const [regSuccess, setRegSuccess] = useState<RegistrationResponse | null>(null);
  const [regError, setRegError] = useState<string | null>(null);
  const [isRegSubmitting, setIsRegSubmitting] = useState(false);

  // Forgot password form state
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotSuccess, setForgotSuccess] = useState<ForgotPasswordResponse | null>(null);
  const [forgotError, setForgotError] = useState<string | null>(null);
  const [isForgotSubmitting, setIsForgotSubmitting] = useState(false);

  // Request Access form state
  const [reqName, setReqName] = useState('');
  const [reqEmail, setReqEmail] = useState('');
  const [reqRole, setReqRole] = useState('FIELD_OFFICER');
  const [reqOrg, setReqOrg] = useState('');
  const [reqDesignation, setReqDesignation] = useState('');
  const [reqReason, setReqReason] = useState('');
  const [reqStateId, setReqStateId] = useState<number | ''>(1);
  const [reqDistrictId, setReqDistrictId] = useState<number | ''>(1);
  const [reqSuccessMsg, setReqSuccessMsg] = useState<string | null>(null);
  const [reqErrorMsg, setReqErrorMsg] = useState<string | null>(null);
  const [isReqSubmitting, setIsReqSubmitting] = useState(false);

  // Modals & Panels
  const [showEvaluatorDrawer, setShowEvaluatorDrawer] = useState(true);

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  // LOGIN Handler
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);
    setIsSubmitting(true);
    try {
      await login(email, password, rememberMe);
      router.push('/dashboard');
    } catch (err: any) {
      setLoginError(err?.message || 'Invalid email or password');
    } finally {
      setIsSubmitting(false);
    }
  };

  // REGISTER Handler
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegError(null);
    setRegSuccess(null);

    if (regPassword !== regConfirmPassword) {
      setRegError('Passwords do not match. Please enter identical credentials.');
      return;
    }
    if (regPassword.length < 8) {
      setRegError('Password must contain at least 8 characters for cybersecurity compliance.');
      return;
    }

    setIsRegSubmitting(true);
    try {
      const res = await api.register({
        name: regName,
        email: regEmail,
        organization: regOrg,
        state_id: regStateId ? Number(regStateId) : null,
        district_id: regDistrictId ? Number(regDistrictId) : null,
        requested_role: regRole,
        password: regPassword,
        confirm_password: regConfirmPassword,
      });
      setRegSuccess(res);
      setRegPassword('');
      setRegConfirmPassword('');
    } catch (err: any) {
      setRegError(err?.message || 'Failed to submit registration.');
    } finally {
      setIsRegSubmitting(false);
    }
  };

  // FORGOT PASSWORD Handler
  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotError(null);
    setForgotSuccess(null);
    setIsForgotSubmitting(true);
    try {
      const res = await api.forgotPassword(forgotEmail);
      setForgotSuccess(res);
    } catch (err: any) {
      setForgotError(err?.message || 'Password recovery dispatch failed.');
    } finally {
      setIsForgotSubmitting(false);
    }
  };

  // REQUEST ACCESS Handler
  const handleRequestAccess = async (e: React.FormEvent) => {
    e.preventDefault();
    setReqErrorMsg(null);
    setReqSuccessMsg(null);
    setIsReqSubmitting(true);
    try {
      await api.submitAccessRequest({
        name: reqName,
        email: reqEmail,
        requested_role: reqRole,
        organization: reqOrg,
        designation: reqDesignation || undefined,
        reason: reqReason,
        state_id: reqStateId ? Number(reqStateId) : null,
        district_id: reqDistrictId ? Number(reqDistrictId) : null,
      });
      setReqSuccessMsg(
        'Your access request has been officially recorded. An Administrator will verify credentials against departmental records.'
      );
      setReqName('');
      setReqEmail('');
      setReqOrg('');
      setReqDesignation('');
      setReqReason('');
    } catch (err: any) {
      setReqErrorMsg(err?.message || 'Failed to submit access request.');
    } finally {
      setIsReqSubmitting(false);
    }
  };



  // Evaluator Persona Quick-Fill
  const handleFillPersona = (personaEmail: string, personaPass: string) => {
    setEmail(personaEmail);
    setPassword(personaPass);
    setLoginError(null);
    setActiveTab('login');
  };

  // Evaluator Persona Direct Login
  const handleDirectDemoLogin = async (personaEmail: string, personaPass: string) => {
    setIsSubmitting(true);
    setLoginError(null);
    try {
      await quickDemoLogin(personaEmail, personaPass);
      router.push('/dashboard');
    } catch (err: any) {
      setLoginError(err?.message || 'Persona authentication failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-800 select-none">
      {/* Top Institutional Hierarchy Bar */}
      <div className="bg-slate-100 border-b border-slate-300 px-4 sm:px-8 py-1 flex items-center justify-between text-[11px] text-slate-600">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-800">JalDrishti Geospatial Decision-Support Portal</span>
          <span className="text-slate-300">|</span>
          <span className="hidden md:inline text-slate-600">
            Watershed Monitoring &amp; Decision Support System
          </span>
        </div>
        <div className="flex items-center space-x-3 text-[11px]">
          <JalDrishtiLogo size="sm" variant="icon" />
          <span className="text-slate-300">|</span>
          <span className="bg-blue-50 text-blue-900 px-2 py-0.2 rounded border border-blue-200 font-bold">
            SIH 26015 | PROTOTYPE SYSTEM
          </span>
        </div>
      </div>

      {/* Main Split Institutional Layout */}
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* ========================================================= */}
        {/* LEFT COLUMN: Cartographic India GIS Visual Panel          */}
        {/* ========================================================= */}
        <div className="hidden lg:flex lg:w-1/2 bg-blue-950 text-white relative flex-col justify-between p-10 overflow-hidden border-r border-slate-300">
          {/* Background Cartographic Vector Overlay */}
          <div className="absolute inset-0 opacity-15 pointer-events-none">
            <svg
              className="w-full h-full text-slate-100"
              viewBox="0 0 800 900"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Subtle Coordinate Grid */}
              <defs>
                <pattern id="split-grid" width="80" height="80" patternUnits="userSpaceOnUse">
                  <path d="M 80 0 L 0 0 0 80" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="3 3" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#split-grid)" />

              {/* Topographic Contours */}
              <path d="M -50 200 Q 200 120, 450 280 T 850 240" stroke="currentColor" strokeWidth="1" strokeDasharray="4 2" />
              <path d="M -50 350 Q 250 260, 500 420 T 850 380" stroke="currentColor" strokeWidth="1" />
              <path d="M -50 500 Q 300 400, 550 560 T 850 520" stroke="currentColor" strokeWidth="1" strokeDasharray="4 2" />
              <path d="M -50 650 Q 350 550, 600 700 T 850 660" stroke="currentColor" strokeWidth="1.2" />

              {/* Dendritic Drainage Networks */}
              <path d="M 400 450 Q 350 360, 300 300 Q 240 220, 200 80" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" />
              <path d="M 460 390 Q 390 350, 350 360" stroke="#38bdf8" strokeWidth="1.5" />
              <path d="M 280 410 Q 310 350, 300 300" stroke="#38bdf8" strokeWidth="1.2" />

              {/* Large Outline of India */}
              <path
                d="M 380 60
                   C 330 90, 300 130, 310 180
                   C 260 180, 220 220, 200 270
                   C 150 290, 120 340, 110 400
                   C 90 450, 60 470, 50 520
                   C 50 560, 90 580, 120 570
                   C 150 570, 180 540, 200 580
                   C 240 640, 290 730, 340 840
                   C 380 910, 400 1020, 410 1040
                   C 420 1020, 440 910, 480 840
                   C 530 730, 580 640, 610 580
                   C 630 540, 660 570, 690 570
                   C 720 580, 760 560, 760 520
                   C 750 470, 710 450, 690 400
                   C 680 340, 650 290, 600 270
                   C 580 220, 540 180, 490 180
                   C 500 130, 470 90, 420 60
                   Z"
                stroke="#60a5fa"
                strokeWidth="2.5"
                strokeDasharray="6 3"
              />

              {/* Coordinate Labels */}
              <text x="30" y="80" fill="currentColor" fontSize="12" fontFamily="monospace">19°12'00"N | 74°32'00"E</text>
              <text x="30" y="840" fill="currentColor" fontSize="12" fontFamily="monospace">CRS: EPSG:4326 (WGS 84)</text>
            </svg>
          </div>

          {/* Top Brand Identity */}
          <div className="relative z-10">
            <JalDrishtiLogo size="lg" variant="horizontal" theme="dark" />
            <div className="mt-6 space-y-2 max-w-lg">
              <p className="text-sm font-semibold text-blue-200 leading-relaxed">
                National Hydrological Decision-Support &amp; Geospatial Monitoring Workstation for Catchment Treatment Planning.
              </p>
              <p className="text-xs text-slate-400 leading-relaxed">
                JalDrishti is designed as an AI-powered decision-support layer that can complement existing geospatial and watershed monitoring infrastructure.
              </p>
            </div>
          </div>

          {/* Core System Capabilities List */}
          <div className="relative z-10 my-8 space-y-3 max-w-md">
            <div className="flex items-start space-x-2.5 text-xs text-slate-300">
              <div className="h-2 w-2 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
              <div>
                <strong className="text-white block font-sans">Multi-Cadre Jurisdictional Governance</strong>
                <span>National, State, District, and Field Micro-Watershed boundaries with strict RBAC enforcement.</span>
              </div>
            </div>
            <div className="flex items-start space-x-2.5 text-xs text-slate-300">
              <div className="h-2 w-2 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
              <div>
                <strong className="text-white block font-sans">Multi-Spectral Remote Sensing &amp; DEM</strong>
                <span>Automated LULC, NDVI vegetative vigor, NDWI surface water spread, and hydrological drainage flow.</span>
              </div>
            </div>
            <div className="flex items-start space-x-2.5 text-xs text-slate-300">
              <div className="h-2 w-2 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
              <div>
                <strong className="text-white block font-sans">DPR Intervention Decision Support</strong>
                <span>Data-driven check dam, farm pond, and contour bund siting with statutory audit tracking.</span>
              </div>
            </div>
          </div>

          {/* Bottom Demarcation */}
          <div className="relative z-10 pt-6 border-t border-blue-900 flex items-center justify-between text-xs text-blue-200">
            <JalDrishtiLogo size="sm" variant="icon" theme="dark" />
            <span className="text-[10px] font-mono text-slate-400">
              DECISION SUPPORT PROTOCOL • SIH 26015
            </span>
          </div>
        </div>

        {/* ========================================================= */}
        {/* RIGHT COLUMN: Clean Institutional Authentication Panel    */}
        {/* ========================================================= */}
        <div className="flex-1 flex flex-col justify-center items-center p-6 sm:p-10 lg:p-12 bg-white">
          <div className="w-full max-w-md space-y-6">
            {/* Top Logo on Mobile (Visible when left column is hidden) */}
            <div className="lg:hidden flex justify-center pb-2">
              <JalDrishtiLogo size="md" variant="horizontal" />
            </div>

            {/* Departmental Card Container */}
            <div className="border border-slate-300 rounded shadow-sm overflow-hidden bg-white">
              {/* Card Header */}
              <div className="bg-slate-100 border-b border-slate-300 px-5 py-3">
                <div className="text-[10px] font-bold tracking-widest text-slate-500 uppercase">
                  WATERSHED DECISION SUPPORT SYSTEM
                </div>
                <div className="text-sm font-bold text-slate-900 mt-0.5">
                  User Authentication &amp; Access Portal
                </div>
              </div>

              {/* Tricolour Accent Line */}
              <div className="h-1 w-full flex">
                <div className="h-full w-1/3 bg-amber-600" />
                <div className="h-full w-1/3 bg-slate-200" />
                <div className="h-full w-1/3 bg-emerald-700" />
              </div>

              {/* Strict Navigation Tabs */}
              <div className="grid grid-cols-4 bg-slate-50 border-b border-slate-200 p-1 gap-1 text-[11px] font-bold uppercase tracking-wider">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('login');
                    setLoginError(null);
                  }}
                  className={`py-1.5 rounded transition-colors text-center ${
                    activeTab === 'login'
                      ? 'bg-blue-900 text-white shadow-2xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
                  }`}
                >
                  LOGIN
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('register');
                    setRegError(null);
                    setRegSuccess(null);
                  }}
                  className={`py-1.5 rounded transition-colors text-center ${
                    activeTab === 'register'
                      ? 'bg-blue-900 text-white shadow-2xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
                  }`}
                >
                  REGISTER
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('forgot');
                    setForgotError(null);
                    setForgotSuccess(null);
                  }}
                  className={`py-1.5 rounded transition-colors text-center ${
                    activeTab === 'forgot'
                      ? 'bg-blue-900 text-white shadow-2xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
                  }`}
                >
                  FORGOT
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('request_access');
                    setReqErrorMsg(null);
                    setReqSuccessMsg(null);
                  }}
                  className={`py-1.5 rounded transition-colors text-center ${
                    activeTab === 'request_access'
                      ? 'bg-blue-900 text-white shadow-2xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
                  }`}
                >
                  ACCESS
                </button>
              </div>

              {/* Tab Contents */}
              <div className="p-6">
                {/* 1. LOGIN MODE */}
                {activeTab === 'login' && (
                  <form onSubmit={handleLogin} className="space-y-4">
                    {loginError && (
                      <div className="p-3 bg-red-50 border-l-4 border-red-600 rounded-r text-xs text-red-900 flex items-start space-x-2">
                        <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <div>
                          <strong className="block">Authentication Denied</strong>
                          <span>{loginError}</span>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1">
                        Email Address / Officer ID *
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                          <Mail className="h-4 w-4" />
                        </div>
                        <input
                          type="email"
                          required
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="e.g. officer@mahawatershed.gov.in"
                          className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900 bg-white"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1">
                        Security Password *
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                          <Lock className="h-4 w-4" />
                        </div>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          required
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="••••••••••••"
                          className="w-full pl-9 pr-9 py-2 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900 bg-white"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-600 pt-1">
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          className="h-3.5 w-3.5 text-blue-900 border-slate-300 rounded"
                        />
                        <span className="text-[11px]">Remember workstation</span>
                      </label>
                      <button
                        type="button"
                        onClick={() => setActiveTab('forgot')}
                        className="text-[11px] font-semibold text-blue-900 hover:underline"
                      >
                        Forgot Password?
                      </button>
                    </div>

                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full py-2.5 px-4 bg-blue-900 hover:bg-blue-950 text-white text-xs font-bold rounded shadow-xs uppercase tracking-wider transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
                    >
                      <span>{isSubmitting ? 'AUTHENTICATING...' : 'LOGIN'}</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>


                  </form>
                )}

                {/* 2. REGISTER MODE */}
                {activeTab === 'register' && (
                  <form onSubmit={handleRegister} className="space-y-3">
                    {regSuccess ? (
                      <div className="p-3 bg-emerald-50 border border-emerald-300 rounded text-xs text-emerald-950 space-y-2">
                        <div className="flex items-center space-x-1.5 text-emerald-900 font-bold">
                          <CheckCircle2 className="h-4 w-4 text-emerald-700" />
                          <span>Registration Queued for Approval</span>
                        </div>
                        <p className="text-[11px] text-emerald-800 leading-relaxed">
                          {regSuccess.message}
                        </p>
                        <div className="pt-1 flex justify-end">
                          <button
                            type="button"
                            onClick={() => setActiveTab('login')}
                            className="px-3 py-1 bg-blue-900 text-white rounded text-xs font-bold"
                          >
                            Return to LOGIN
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {regError && (
                          <div className="p-2.5 bg-red-50 border border-red-300 rounded text-xs text-red-900">
                            {regError}
                          </div>
                        )}

                        <div>
                          <label className="block text-xs font-bold text-slate-800 mb-1">
                            Full Name *
                          </label>
                          <input
                            type="text"
                            required
                            value={regName}
                            onChange={(e) => setRegName(e.target.value)}
                            placeholder="e.g. Dr. Rajesh Verma"
                            className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-slate-800 mb-1">
                            Email Address / Officer ID *
                          </label>
                          <input
                            type="email"
                            required
                            value={regEmail}
                            onChange={(e) => setRegEmail(e.target.value)}
                            placeholder="officer@department.gov.in"
                            className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">
                              Department / Agency *
                            </label>
                            <input
                              type="text"
                              required
                              value={regOrg}
                              onChange={(e) => setRegOrg(e.target.value)}
                              placeholder="e.g. DRDA / Agency"
                              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">
                              Requested Role *
                            </label>
                            <select
                              value={regRole}
                              onChange={(e) => setRegRole(e.target.value)}
                              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900 font-semibold"
                            >
                              <option value="FIELD_OFFICER">Field Officer</option>
                              <option value="DISTRICT_OFFICER">District Officer</option>
                              <option value="STATE_OFFICER">State Officer</option>
                              <option value="ANALYST">Analyst</option>
                            </select>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">
                              Password (Min 8 Chars) *
                            </label>
                            <input
                              type="password"
                              required
                              value={regPassword}
                              onChange={(e) => setRegPassword(e.target.value)}
                              placeholder="••••••••••••"
                              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">
                              Confirm Password *
                            </label>
                            <input
                              type="password"
                              required
                              value={regConfirmPassword}
                              onChange={(e) => setRegConfirmPassword(e.target.value)}
                              placeholder="••••••••••••"
                              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-blue-900 text-slate-900"
                            />
                          </div>
                        </div>

                        <div className="p-2 bg-blue-50 border border-blue-200 rounded text-[11px] text-blue-900">
                          Registration creates an unactivated profile. An Administrator reviews credentials before GIS access is granted.
                        </div>

                        <button
                          type="submit"
                          disabled={isRegSubmitting}
                          className="w-full py-2 bg-blue-900 hover:bg-blue-950 text-white text-xs font-bold rounded shadow-xs uppercase tracking-wider"
                        >
                          {isRegSubmitting ? 'SUBMITTING...' : 'REGISTER ACCOUNT'}
                        </button>
                      </>
                    )}
                  </form>
                )}

                {/* 3. FORGOT PASSWORD MODE */}
                {activeTab === 'forgot' && (
                  <form onSubmit={handleForgotPassword} className="space-y-3">
                    {forgotSuccess ? (
                      <div className="p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-900 space-y-2">
                        <div className="font-bold text-blue-950">Recovery Request Recorded</div>
                        <p className="text-[11px] leading-relaxed">{forgotSuccess.message}</p>
                        <div className="font-mono text-[10px] text-slate-700 bg-white p-2 rounded border border-blue-100">
                          Helpline: {forgotSuccess.support_contact}
                        </div>
                        <button
                          type="button"
                          onClick={() => setActiveTab('login')}
                          className="px-3 py-1 bg-blue-900 text-white rounded text-xs font-bold mt-2"
                        >
                          Return to LOGIN
                        </button>
                      </div>
                    ) : (
                      <>
                        {forgotError && (
                          <div className="p-2.5 bg-red-50 border border-red-300 rounded text-xs text-red-900">
                            {forgotError}
                          </div>
                        )}

                        <div>
                          <label className="block text-xs font-bold text-slate-800 mb-1">
                            Registered Email Address *
                          </label>
                          <input
                            type="email"
                            required
                            value={forgotEmail}
                            onChange={(e) => setForgotEmail(e.target.value)}
                            placeholder="officer@agency.gov.in"
                            className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded text-slate-900"
                          />
                        </div>

                        <div className="p-2.5 bg-amber-50 border border-amber-200 rounded text-[11px] text-amber-950">
                          <strong>GIGW 3.0 Cybersecurity Protocol:</strong> Automated reset links are not dispatched over unauthenticated email. Password resets require departmental verification.
                        </div>

                        <div className="p-2 bg-slate-50 border border-slate-200 rounded text-[10px] font-mono text-slate-600 space-y-0.5">
                          <div>Nodal Admin: admin@jaldrishti.gov.in</div>
                          <div>National Helpdesk: 1800-111-JAL</div>
                        </div>

                        <button
                          type="submit"
                          disabled={isForgotSubmitting}
                          className="w-full py-2 bg-blue-900 hover:bg-blue-950 text-white text-xs font-bold rounded uppercase tracking-wider"
                        >
                          {isForgotSubmitting ? 'DISPATCHING...' : 'SUBMIT RECOVERY REQUEST'}
                        </button>
                      </>
                    )}
                  </form>
                )}

                {/* 4. REQUEST ACCESS MODE */}
                {activeTab === 'request_access' && (
                  <form onSubmit={handleRequestAccess} className="space-y-3">
                    {reqSuccessMsg ? (
                      <div className="p-3 bg-emerald-50 border border-emerald-300 rounded text-xs text-emerald-950 space-y-2">
                        <div className="font-bold text-emerald-900">Access Request Logged</div>
                        <p className="text-[11px]">{reqSuccessMsg}</p>
                        <button
                          type="button"
                          onClick={() => setActiveTab('login')}
                          className="px-3 py-1 bg-blue-900 text-white rounded text-xs font-bold"
                        >
                          Return to LOGIN
                        </button>
                      </div>
                    ) : (
                      <>
                        {reqErrorMsg && (
                          <div className="p-2.5 bg-red-50 border border-red-300 rounded text-xs text-red-900">
                            {reqErrorMsg}
                          </div>
                        )}

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">Name *</label>
                            <input
                              type="text"
                              required
                              value={reqName}
                              onChange={(e) => setReqName(e.target.value)}
                              placeholder="Officer Name"
                              className="w-full px-2 py-1 text-xs border border-slate-300 rounded"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">Email Address *</label>
                            <input
                              type="email"
                              required
                              value={reqEmail}
                              onChange={(e) => setReqEmail(e.target.value)}
                              placeholder="officer@agency.gov.in"
                              className="w-full px-2 py-1 text-xs border border-slate-300 rounded"
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">Role Scope *</label>
                            <select
                              value={reqRole}
                              onChange={(e) => setReqRole(e.target.value)}
                              className="w-full px-2 py-1 text-xs border border-slate-300 rounded"
                            >
                              <option value="FIELD_OFFICER">Field Officer</option>
                              <option value="DISTRICT_OFFICER">District Officer</option>
                              <option value="STATE_OFFICER">State Officer</option>
                              <option value="ANALYST">Analyst</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-800 mb-1">Agency *</label>
                            <input
                              type="text"
                              required
                              value={reqOrg}
                              onChange={(e) => setReqOrg(e.target.value)}
                              placeholder="State Agency"
                              className="w-full px-2 py-1 text-xs border border-slate-300 rounded"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-slate-800 mb-1">Justification Mandate *</label>
                          <textarea
                            rows={2}
                            required
                            value={reqReason}
                            onChange={(e) => setReqReason(e.target.value)}
                            placeholder="Specify government order or watershed mandate..."
                            className="w-full px-2 py-1 text-xs border border-slate-300 rounded"
                          />
                        </div>

                        <button
                          type="submit"
                          disabled={isReqSubmitting}
                          className="w-full py-2 bg-emerald-800 hover:bg-emerald-900 text-white text-xs font-bold rounded uppercase tracking-wider"
                        >
                          {isReqSubmitting ? 'SUBMITTING...' : 'SUBMIT ACCESS REQUEST'}
                        </button>
                      </>
                    )}
                  </form>
                )}
              </div>
            </div>

            {/* SIH Evaluator Quick-Fill Drawer */}
            <div className="border border-slate-300 rounded overflow-hidden bg-white shadow-2xs">
              <button
                type="button"
                onClick={() => setShowEvaluatorDrawer(!showEvaluatorDrawer)}
                className="w-full px-3 py-2 bg-slate-100 hover:bg-slate-200/80 flex items-center justify-between text-left transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-emerald-600 animate-pulse" />
                  <span className="text-[11px] font-bold text-slate-900 uppercase tracking-wider">
                    SIH 26015 Jury &amp; Evaluator Test Cadres (5 Roles)
                  </span>
                </div>
                {showEvaluatorDrawer ? <ChevronUp className="h-3.5 w-3.5 text-slate-500" /> : <ChevronDown className="h-3.5 w-3.5 text-slate-500" />}
              </button>

              {showEvaluatorDrawer && (
                <div className="p-3 bg-slate-50/80 space-y-2 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {demoAccounts.map((acc) => (
                      <div
                        key={acc.email}
                        className="p-2 bg-white rounded border border-slate-200 hover:border-slate-300 transition-colors flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-[10px] text-blue-900">{acc.role}</span>
                            <span className="text-[9px] font-mono text-slate-400">Demo</span>
                          </div>
                          <div className="font-bold text-slate-900 text-xs truncate mt-0.5">{acc.name}</div>
                          <div className="text-[10px] text-slate-500 truncate">{acc.jurisdiction}</div>
                        </div>

                        <div className="flex items-center space-x-1 pt-1.5 mt-1 border-t border-slate-100">
                          <button
                            type="button"
                            onClick={() => handleFillPersona(acc.email, acc.demo_password)}
                            className="flex-1 py-0.5 px-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded text-[10px] font-semibold"
                          >
                            Fill
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDirectDemoLogin(acc.email, acc.demo_password)}
                            className="flex-1 py-0.5 px-1 bg-blue-900 hover:bg-blue-950 text-white rounded text-[10px] font-bold"
                          >
                            Test Login
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>



      {/* Government Footer */}
      <footer className="bg-white border-t border-slate-300 py-3 px-4 sm:px-8 text-center text-[11px] text-slate-600">
        <div className="max-w-4xl mx-auto space-y-1">
          <p className="font-semibold text-slate-800">
            JalDrishti — Watershed Monitoring &amp; Geospatial Decision Support System | Smart India Hackathon (SIH 26015)
          </p>
          <p className="text-[10px] text-slate-500">
            JalDrishti is designed as an AI-powered decision-support layer to complement existing geospatial and watershed monitoring infrastructure.
          </p>
        </div>
      </footer>
    </div>
  );
}
