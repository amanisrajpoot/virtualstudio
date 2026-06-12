"use client";

import { useEffect, useState } from "react";
import { fetchRenderJobs } from "@/lib/api";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

export default function QueuePage() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    fetchRenderJobs().then(data => setJobs(data.jobs)).catch(() => {});
  }, []);

  const orchestratorStages = [
    "Compile", "Planning", "Dialogue", "Audio", "Assets", "Rendering", "Export"
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto h-full overflow-auto bg-slate-50">
      <h1 className="text-2xl font-bold text-slate-800 mb-8">Render Queue</h1>
      
      <div className="space-y-6">
        {jobs.map((job: any) => (
          <div key={job.job_id} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="font-semibold text-lg text-slate-800">{job.story}</h3>
                <span className="text-sm text-slate-500">ID: {job.job_id}</span>
              </div>
              <div className={`px-4 py-1.5 rounded-full text-sm font-bold flex items-center space-x-2 ${
                job.status === "Completed" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"
              }`}>
                {job.status === "Rendering" && <Loader2 size={16} className="animate-spin" />}
                {job.status === "Completed" && <CheckCircle2 size={16} />}
                <span>{job.status}</span>
              </div>
            </div>

            {/* Orchestrator Stages Pipeline */}
            <div className="flex items-center justify-between border-t border-slate-100 pt-6">
              {orchestratorStages.map((stage, idx) => {
                const isCompleted = job.status === "Completed" || (job.status === "Rendering" && idx < 5);
                const isCurrent = job.status === "Rendering" && idx === 5;
                
                return (
                  <div key={stage} className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-2 ${
                      isCompleted ? "bg-green-500 text-white" :
                      isCurrent ? "bg-blue-500 text-white animate-pulse" :
                      "bg-slate-200 text-slate-400"
                    }`}>
                      {isCompleted ? <CheckCircle2 size={16} /> : 
                       isCurrent ? <Loader2 size={16} className="animate-spin" /> : 
                       <Circle size={12} />}
                    </div>
                    <span className={`text-xs font-medium ${isCurrent ? "text-blue-600" : isCompleted ? "text-slate-800" : "text-slate-400"}`}>
                      {stage}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
