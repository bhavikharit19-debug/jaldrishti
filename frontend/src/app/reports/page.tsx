'use client';
import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { WatershedReport } from '@/types';
import { api } from '@/services/api';
import { Printer, ArrowLeft, ShieldCheck, CheckCircle2, AlertTriangle, FileText, Download } from 'lucide-react';
import Link from 'next/link';
import JalDrishtiLogo from '@/components/common/JalDrishtiLogo';

function ReportContent() {
  const searchParams = useSearchParams();
  const idStr = searchParams.get('id');
  const watershedId = idStr ? parseInt(idStr, 10) : 1;

  const [report, setReport] = useState<WatershedReport | null>(null);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [risks, setRisks] = useState<any[]>([]);
  const [interventions, setInterventions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getReport(watershedId).catch(() => null),
      api.getPredictions(watershedId).catch(() => ({ predictions: [] })),
      api.getRisks(watershedId).catch(() => ({ risks: [] })),
      api.getInterventions(watershedId).catch(() => [])
    ]).then(([rep, pred, rsk, intv]) => {
      setReport(rep);
      setPredictions(pred?.predictions || []);
      setRisks(rsk?.risks || []);
      setInterventions(intv || []);
      setLoading(false);
    });
  }, [watershedId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="text-slate-600 font-semibold text-xs">Compiling Diagnostic Report...</div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="text-red-700 font-semibold text-xs">Report could not be retrieved.</div>
      </div>
    );
  }

  const { watershed, health_score } = report;

  return (
    <div className="min-h-screen bg-slate-100 py-6 px-4 sm:px-6 lg:px-8 font-sans text-slate-900 select-none">
      {/* Top action bar (hidden during print) */}
      <div className="max-w-4xl mx-auto mb-4 flex items-center justify-between print:hidden">
        <Link
          href="/"
          className="inline-flex items-center space-x-1.5 text-xs font-bold text-slate-700 hover:text-blue-900 bg-white px-3 py-1.5 rounded border border-slate-300 shadow-2xs"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Return to GIS Workstation</span>
        </Link>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => window.print()}
            className="inline-flex items-center space-x-1.5 text-xs font-bold text-white bg-blue-900 hover:bg-blue-950 px-4 py-1.5 rounded shadow-xs transition-colors"
          >
            <Printer className="h-3.5 w-3.5" />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Printable Report Document Paper */}
      <div className="max-w-4xl mx-auto bg-white border border-slate-300 shadow-sm p-8 sm:p-12 print:border-none print:shadow-none print:p-0 space-y-6">
        {/* Top Report Header Strip */}
        <div className="border-b border-slate-300 pb-3">
          <div className="flex items-center justify-between text-[11px] text-slate-600 mb-2">
            <span className="font-semibold text-slate-800">JALDRISHTI WATERSHED MONITORING &amp; GEOSPATIAL DECISION SUPPORT SYSTEM</span>
            <span className="font-mono text-[10px] bg-slate-100 px-2 py-0.5 rounded border border-slate-200">SIH 26015 | PROTOTYPE</span>
          </div>

          <div className="flex items-center justify-between pt-2">
            <JalDrishtiLogo size="lg" variant="horizontal" />
            <div className="text-right text-xs text-slate-600 font-mono">
              <span className="block font-bold text-slate-900">
                DATE: {new Date(report.generated_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
              </span>
              <span className="block">CATCHMENT CODE: {watershed.code}</span>
              <span className="block text-[10px] text-slate-500">PROTOTYPE DECISION DOSSIER</span>
            </div>
          </div>
        </div>

        {/* Tricolour Accent Line */}
        <div className="h-1 w-full flex">
          <div className="h-full w-1/3 bg-amber-600" />
          <div className="h-full w-1/3 bg-slate-200" />
          <div className="h-full w-1/3 bg-emerald-700" />
        </div>

        {/* Report Title */}
        <div className="text-center pb-4 border-b border-slate-200">
          <h1 className="text-lg font-black uppercase tracking-wider text-slate-950">
            JalDrishti Watershed Assessment &amp; Decision Report
          </h1>
          <p className="text-xs text-slate-600 font-medium mt-1">
            Complementary Decision-Support Layer for Watershed Treatment Planning
          </p>
        </div>

        {/* Section 1: Geographic & Administrative Profile */}
        <div>
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-2.5">
            1. Administrative &amp; Geographic Profile
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-slate-50 p-3 rounded border border-slate-200 font-mono">
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">Micro-Watershed:</span>
              <strong className="text-slate-900">{watershed.name}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">State &amp; District:</span>
              <strong className="text-slate-900">{watershed.district_name}, {watershed.state_name}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">Catchment Area:</span>
              <strong className="text-blue-900">{watershed.area_hectares ? `${watershed.area_hectares.toLocaleString()} Ha` : '—'}</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">River Basin:</span>
              <strong className="text-slate-900">{watershed.river_basin || 'Godavari Basin'}</strong>
            </div>
          </div>
        </div>

        {/* Section 2: Health Score & Biophysical Indicators */}
        <div>
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-2.5">
            2. Biophysical Indicator Synthesis &amp; Health Score
          </h2>
          <div className="flex items-center justify-between bg-slate-50 p-3 rounded border border-slate-200 mb-3 text-xs">
            <div>
              <span className="text-slate-500 text-[11px] block font-bold uppercase">Composite Health Score</span>
              <div className="text-2xl font-black text-blue-950 font-mono mt-0.5">
                {Math.round(health_score.overall_health_score)} / 100
                <span className="ml-2 text-xs font-extrabold px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300 font-sans">
                  {health_score.category_rating}
                </span>
              </div>
            </div>
            <div className="text-right text-xs">
              <span className="text-slate-500 block">Vulnerability Rating</span>
              <span className="font-bold text-slate-900">{watershed.risk_level} RISK</span>
            </div>
          </div>

          <table className="w-full text-left text-xs border border-slate-300 divide-y divide-slate-200">
            <thead className="bg-slate-100 text-[10px] font-bold text-slate-700 uppercase">
              <tr>
                <th className="p-2">Indicator Parameter</th>
                <th className="p-2">Category</th>
                <th className="p-2 text-center">Assigned Weight</th>
                <th className="p-2 text-center">Score (0-100)</th>
                <th className="p-2 text-right">Condition Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-xs">
              {health_score.components.map((c, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="p-2 font-semibold text-slate-900">{c.name}</td>
                  <td className="p-2 text-slate-500">{c.category}</td>
                  <td className="p-2 text-center font-mono">{(c.weight * 100).toFixed(0)}%</td>
                  <td className="p-2 text-center font-mono font-bold text-blue-900">{Math.round(c.score)}</td>
                  <td className="p-2 text-right font-bold text-slate-800">{c.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Section 3: Multi-Hazard Vulnerability Register */}
        <div>
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-2.5">
            3. Multi-Hazard Environmental Risk Evaluation
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {risks.slice(0, 4).map((r: any) => (
              <div key={r.id} className="p-3 bg-slate-50 border border-slate-200 rounded space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 font-mono">
                    {r.risk_category.replace(/_/g, ' ')}
                  </span>
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-extrabold bg-amber-100 text-amber-900 border border-amber-300">
                    {r.risk_level}
                  </span>
                </div>
                <p className="text-slate-600 text-[11px] leading-snug">{r.evidence_summary}</p>
                <div className="text-[10px] text-slate-500 pt-1 font-mono">
                  Primary Trigger: {r.primary_driver}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 4: Machine Learning Predictive Outlook */}
        <div>
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-2.5">
            4. Prototype Predictive Intelligence (6–12 Month Outlook)
          </h2>
          <div className="overflow-x-auto border border-slate-200 rounded">
            <table className="w-full text-left text-xs text-slate-800 divide-y divide-slate-200">
              <thead className="bg-slate-50 text-[10px] font-bold text-slate-600 uppercase">
                <tr>
                  <th className="p-2">Target Metric</th>
                  <th className="p-2">Projected Value</th>
                  <th className="p-2">95% Confidence Interval</th>
                  <th className="p-2">Contributing Factors</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-xs font-mono">
                {predictions.slice(0, 3).map((p: any) => (
                  <tr key={p.id}>
                    <td className="p-2 font-bold text-slate-900">{p.target_metric.replace(/_/g, ' ')}</td>
                    <td className="p-2 font-bold text-blue-900">{p.predicted_value}</td>
                    <td className="p-2 text-slate-600">[{p.confidence_lower} – {p.confidence_upper}]</td>
                    <td className="p-2 text-[11px] font-sans text-slate-600">{p.rationale}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 5: Recommended DPR Interventions */}
        <div>
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-2.5">
            5. Recommended DPR Interventions &amp; Cost Estimates
          </h2>
          <div className="space-y-2 text-xs">
            {report.top_recommendations.map((rec) => (
              <div key={rec.id} className="p-3 bg-slate-50 rounded border border-slate-200 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-950 font-mono">
                    {rec.intervention_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-amber-50 text-amber-900 border border-amber-300">
                    {rec.priority} PRIORITY
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1">
                  <div>
                    <span className="text-slate-500 font-semibold">Problem Statement: </span>
                    <span className="text-slate-700">{rec.problem_statement}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 font-semibold">Biophysical Evidence: </span>
                    <span className="text-slate-700">{rec.evidence_basis}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-1 border-t border-slate-200 text-[11px]">
                  <span className="text-slate-600">Expected Impact: {rec.expected_impact}</span>
                  <span className="font-mono font-bold text-blue-900">{rec.estimated_cost_inr || '₹4,50,000'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 6: Existing Structures & Beneficiaries */}
        <div>
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-2.5">
            6. Existing Structural Interventions &amp; Beneficiaries
          </h2>
          <div className="grid grid-cols-3 gap-3 text-xs bg-slate-50 p-3 rounded border border-slate-200 font-mono text-center">
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">Active Structures:</span>
              <strong className="text-slate-900 text-sm">{interventions.length} Sites</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">Completed Works:</span>
              <strong className="text-emerald-800 text-sm">{report.completed_interventions_count} Sanctioned</strong>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block font-sans">Estimated Beneficiaries:</span>
              <strong className="text-blue-900 text-sm">{report.total_beneficiaries} Farming Families</strong>
            </div>
          </div>
        </div>

        {/* Review & Approval Section */}
        <div className="pt-4 border-t border-slate-300 text-[10px] text-slate-500 space-y-3">
          <p>
            * Decision-Support Notice: Generated via JalDrishti geospatial decision-support layer. Recommended interventions represent prototype decision-support estimations designed to complement existing watershed monitoring infrastructure. Ground topographical verification and Gram Sabha sanction are recommended prior to civil works execution.
          </p>

          <div className="pt-2">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">Review &amp; Approval Section</h3>
            <div className="grid grid-cols-2 gap-8 pt-4 text-xs text-slate-700">
              <div className="border-t border-slate-400 pt-2 text-center">
                <strong className="block text-slate-900">Project Officer / Decision-Support Reviewer</strong>
                <span className="text-[10px] text-slate-500">Watershed Development Planning Cadre</span>
              </div>
              <div className="border-t border-slate-400 pt-2 text-center">
                <strong className="block text-slate-900">Geospatial &amp; Remote Sensing Analyst</strong>
                <span className="text-[10px] text-slate-500">Watershed Monitoring &amp; Evaluation</span>
              </div>
            </div>
          </div>

          <div className="pt-3 flex justify-between items-center text-slate-400 font-mono text-[9px] border-t border-slate-200">
            <span>DECISION-SUPPORT PROTOTYPE</span>
            <span>SMART INDIA HACKATHON (SIH 26015)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ReportPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs">Loading report...</div>}>
      <ReportContent />
    </Suspense>
  );
}
