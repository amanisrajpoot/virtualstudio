"use client";

import { useState, useEffect } from "react";
import { fetchMetrics, fetchFailures, fetchStoryHealth } from "@/lib/api";
import { Activity, AlertTriangle, CheckCircle2, HeartPulse, Clock, Database, Search } from "lucide-react";

export default function DiagnosticsPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [failures, setFailures] = useState<any>(null);
  const [healthId, setHealthId] = useState("");
  const [healthData, setHealthData] = useState<any>(null);

  useEffect(() => {
    fetchMetrics().then(setMetrics).catch(() => {});
    fetchFailures().then(setFailures).catch(() => {});
  }, []);

  const checkHealth = async () => {
    if (!healthId) return;
    try {
      const data = await fetchStoryHealth(healthId);
      setHealthData(data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 overflow-auto p-8">
      <h1 className="text-2xl font-bold text-slate-800 mb-6 flex items-center">
        <Activity className="mr-3 text-indigo-500" /> StoryForge Observability
      </h1>

      {/* Metrics Row */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center">
            <span className="text-sm font-bold text-slate-500 uppercase">Stories Created</span>
            <span className="text-4xl font-bold text-slate-800 mt-2">{metrics.funnel.stories_created}</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center">
            <span className="text-sm font-bold text-slate-500 uppercase">Previews Gen</span>
            <span className="text-4xl font-bold text-indigo-600 mt-2">{metrics.funnel.previews_generated}</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center">
            <span className="text-sm font-bold text-slate-500 uppercase">Renders Started</span>
            <span className="text-4xl font-bold text-emerald-600 mt-2">{metrics.funnel.renders_started}</span>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center">
            <span className="text-sm font-bold text-slate-500 uppercase">Preview Hit Rate</span>
            <span className="text-4xl font-bold text-blue-500 mt-2">{metrics.cache.preview_cache_hit_rate.toFixed(1)}%</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        {/* Latency Leaderboard */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="bg-slate-50 p-4 border-b border-slate-200 flex items-center">
            <Clock size={18} className="text-slate-500 mr-2" />
            <h2 className="text-sm font-bold text-slate-700 uppercase">P95 Latency Leaderboard</h2>
          </div>
          <div className="p-4 space-y-4">
            {metrics?.aggregates.map((agg: any) => (
              <div key={agg.metric_name} className="flex justify-between items-center p-3 bg-slate-50 rounded border border-slate-100">
                <span className="font-medium text-slate-700">{agg.metric_name}</span>
                <span className={`font-bold ${agg.p95 > 1000 ? 'text-rose-500' : 'text-emerald-500'}`}>
                  {agg.p95.toFixed(1)}ms
                </span>
              </div>
            ))}
            {!metrics?.aggregates.length && <div className="text-sm text-slate-400 text-center py-4">No metrics recorded yet.</div>}
          </div>
        </div>

        {/* Failures */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="bg-slate-50 p-4 border-b border-slate-200 flex items-center">
            <AlertTriangle size={18} className="text-amber-500 mr-2" />
            <h2 className="text-sm font-bold text-slate-700 uppercase">Most Common Failures</h2>
          </div>
          <div className="p-4 space-y-4">
             {failures?.failures.map((f: any, i: number) => (
               <div key={i} className="flex flex-col p-3 bg-rose-50 rounded border border-rose-100">
                 <div className="flex justify-between items-center mb-1">
                   <span className="font-bold text-rose-800">{f.error_type}</span>
                   <span className="bg-rose-200 text-rose-800 px-2 rounded-full text-xs font-bold">{f.count}x</span>
                 </div>
                 <span className="text-sm text-rose-600">{f.details}</span>
               </div>
             ))}
             {!failures?.failures.length && <div className="text-sm text-slate-400 text-center py-4">No failures recorded yet.</div>}
          </div>
        </div>

      </div>

      {/* Health Inspector */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-8">
        <div className="bg-slate-50 p-4 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center">
            <HeartPulse size={18} className="text-rose-500 mr-2" />
            <h2 className="text-sm font-bold text-slate-700 uppercase">Health Inspector</h2>
          </div>
          <div className="flex space-x-2">
            <input 
              type="text" 
              placeholder="Enter Story ID..." 
              className="text-sm border border-slate-300 rounded px-3 py-1 outline-none"
              value={healthId}
              onChange={(e) => setHealthId(e.target.value)}
            />
            <button onClick={checkHealth} className="bg-indigo-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-indigo-700">Check</button>
          </div>
        </div>
        
        {healthData ? (
          <div className="p-6 flex flex-col md:flex-row space-y-6 md:space-y-0 md:space-x-8">
            <div className="flex flex-col items-center justify-center border-r border-slate-200 pr-8">
              <span className="text-sm font-bold text-slate-500 uppercase mb-2">Final Score</span>
              <div className={`w-32 h-32 rounded-full flex items-center justify-center border-8 ${healthData.final_score > 80 ? 'border-emerald-400 text-emerald-600' : 'border-amber-400 text-amber-600'}`}>
                <span className="text-4xl font-bold">{healthData.final_score}</span>
              </div>
            </div>
            
            <div className="flex-1 grid grid-cols-2 gap-4">
              {['assets', 'characters', 'world', 'timeline', 'dialogue'].map(dim => (
                <div key={dim} className="flex justify-between items-center p-3 bg-slate-50 rounded border border-slate-100">
                  <span className="capitalize text-sm font-bold text-slate-600">{dim}</span>
                  <span className={`text-sm font-bold ${healthData[`${dim}_score`] < 100 ? 'text-rose-500' : 'text-emerald-500'}`}>
                    {healthData[`${dim}_score`]} / 100
                  </span>
                </div>
              ))}
            </div>

            <div className="flex-1">
              <h3 className="text-sm font-bold text-slate-700 mb-3 uppercase">Warnings</h3>
              <ul className="space-y-2">
                {healthData.warnings.map((w: string, i: number) => (
                  <li key={i} className="text-sm text-amber-700 bg-amber-50 p-2 rounded border border-amber-200 flex items-start">
                    <AlertTriangle size={16} className="mr-2 shrink-0 mt-0.5" />
                    {w}
                  </li>
                ))}
                {healthData.warnings.length === 0 && <li className="text-sm text-emerald-600 flex items-center"><CheckCircle2 size={16} className="mr-2"/> No warnings detected.</li>}
              </ul>
            </div>

          </div>
        ) : (
          <div className="p-8 flex flex-col items-center justify-center text-slate-400">
            <Search size={48} className="mb-4 text-slate-200" />
            <p>Input a Story ID to inspect its multidimensional health score.</p>
          </div>
        )}
      </div>

    </div>
  );
}
