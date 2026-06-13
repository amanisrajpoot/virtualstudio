"use client";

import { useState, useEffect } from "react";
import { fetchRenderJobs, fetchRenderMetrics } from "@/lib/api";
import { Server, Activity, AlertTriangle, CheckCircle, Clock, Video } from "lucide-react";

export default function RenderQueueDashboard() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetchRenderJobs().then(res => setJobs(res.jobs || []));
    fetchRenderMetrics().then(res => setMetrics(res));
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-slate-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center">
              <Server className="mr-3 text-indigo-500" />
              Render Control Plane
            </h1>
            <p className="text-slate-500 mt-1">Monitor distributed workers and active render jobs.</p>
          </div>
        </div>

        {/* Metrics Bar */}
        {metrics && (
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Queued Jobs</p>
                <p className="text-2xl font-bold text-slate-800">{metrics.queued_jobs}</p>
              </div>
              <Clock className="text-indigo-400" size={24} />
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Active Jobs</p>
                <p className="text-2xl font-bold text-slate-800">{metrics.active_jobs}</p>
              </div>
              <Activity className="text-blue-400" size={24} />
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Completed</p>
                <p className="text-2xl font-bold text-slate-800">{metrics.completed_jobs}</p>
              </div>
              <CheckCircle className="text-emerald-400" size={24} />
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Failed</p>
                <p className="text-2xl font-bold text-slate-800">{metrics.failed_jobs}</p>
              </div>
              <AlertTriangle className="text-rose-400" size={24} />
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
            <h2 className="font-bold text-slate-700 flex items-center">
              <Video className="mr-2 text-slate-400" size={18} /> Render Queue
            </h2>
          </div>
          
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 font-medium">Job ID / Project</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Priority</th>
                <th className="px-6 py-3 font-medium">Worker</th>
                <th className="px-6 py-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-400">No jobs in queue.</td>
                </tr>
              ) : jobs.map((j) => (
                <tr key={j.job_id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-800">{j.job_id.substring(0, 8)}...</div>
                    <div className="text-xs text-slate-500 mt-1">{j.project_id} (v{j.snapshot_version})</div>
                    {j.approval_status !== "approved" && (
                       <div className="mt-1 flex items-center text-[10px] font-bold text-amber-600 bg-amber-50 w-max px-1.5 py-0.5 rounded">
                         <AlertTriangle size={10} className="mr-1" /> UNAPPROVED RENDER
                       </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                      j.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                      j.status === 'failed' ? 'bg-rose-100 text-rose-700' :
                      j.status === 'queued' ? 'bg-slate-100 text-slate-700' :
                      'bg-indigo-100 text-indigo-700'
                    }`}>
                      {j.status.toUpperCase()}
                    </span>
                    {j.retry_count > 0 && <div className="text-xs text-rose-500 mt-1">Retries: {j.retry_count}/{j.max_retries}</div>}
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-mono text-slate-600">{j.priority}</div>
                  </td>
                  <td className="px-6 py-4">
                    {j.worker_id ? (
                      <span className="font-mono text-xs bg-slate-100 px-2 py-1 rounded text-slate-600">{j.worker_id}</span>
                    ) : (
                      <span className="text-slate-400 italic">Unassigned</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {new Date(j.submitted_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
