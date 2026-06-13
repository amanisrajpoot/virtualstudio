"use client";

import { useState, useEffect } from "react";
import { fetchProjectsList, fetchMockUsers, approveRevision } from "@/lib/api";
import { Folder, Plus, Clock, Video, Archive, ArrowRight, History, GitCommit, CheckCircle, AlertTriangle, UserCircle } from "lucide-react";
import Link from "next/link";

export default function ProjectsDashboard() {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [mockUsers, setMockUsers] = useState<any[]>([]);
  const [activeUser, setActiveUser] = useState<any>(null);

  useEffect(() => {
    fetchProjectsList().then(res => setProjects(res.projects || []));
    fetchMockUsers().then(res => {
      const users = res.users || [];
      setMockUsers(users);
      if (users.length > 0) setActiveUser(users[0]); // Default to Owner
    });
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-slate-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center">
              <Folder className="mr-3 text-indigo-500" />
              Project Runtime
            </h1>
            <p className="text-slate-500 mt-1">Manage your StoryForge projects and semantic history.</p>
          </div>
          <div className="flex items-center space-x-4">
            {activeUser && (
              <div className="flex items-center bg-white border border-slate-200 rounded-lg px-3 py-1.5 shadow-sm">
                <UserCircle size={16} className="text-slate-400 mr-2" />
                <span className="text-sm font-medium text-slate-600 mr-2">Role:</span>
                <select 
                  className="bg-transparent text-sm font-bold text-indigo-600 outline-none"
                  value={activeUser.user_id}
                  onChange={(e) => setActiveUser(mockUsers.find(u => u.user_id === e.target.value))}
                >
                  {mockUsers.map(u => (
                    <option key={u.user_id} value={u.user_id}>{u.name}</option>
                  ))}
                </select>
              </div>
            )}
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium flex items-center shadow-sm transition-colors">
              <Plus size={18} className="mr-2" />
              New Project
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Project Grid */}
          <div className="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {projects.length === 0 ? (
              <div className="col-span-2 bg-white border-2 border-dashed border-slate-200 rounded-xl p-12 text-center text-slate-500">
                No projects found. Create one to start building.
              </div>
            ) : projects.map((p, i) => (
              <div 
                key={i} 
                className={`bg-white rounded-xl border ${selectedProject?.project_id === p.project_id ? 'border-indigo-500 ring-2 ring-indigo-50' : 'border-slate-200 hover:border-indigo-300'} p-5 shadow-sm cursor-pointer transition-all`}
                onClick={() => setSelectedProject(p)}
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold text-slate-800 text-lg">{p.name || p.project_id}</h3>
                  <div className="bg-slate-100 text-slate-500 text-xs px-2 py-1 rounded-md font-mono">
                    v{p.graph_version || 1}
                  </div>
                </div>
                
                {/* Approval Status Badge */}
                {p.approvals && p.approvals.find((a: any) => a.revision_id === `rev_${p.active_snapshot_version || p.graph_version}`)?.status === 'approved' ? (
                  <div className="flex items-center text-xs font-bold text-emerald-600 bg-emerald-50 w-max px-2 py-1 rounded mb-3">
                    <CheckCircle size={12} className="mr-1" /> APPROVED
                  </div>
                ) : (
                  <div className="flex items-center text-xs font-bold text-amber-600 bg-amber-50 w-max px-2 py-1 rounded mb-3">
                    <AlertTriangle size={12} className="mr-1" /> NOT APPROVED
                  </div>
                )}

                <p className="text-sm text-slate-500 mb-4 line-clamp-2">{p.description || "No description provided."}</p>
                <div className="flex items-center text-xs text-slate-400 font-medium space-x-4">
                   <div className="flex items-center"><Clock size={14} className="mr-1"/> {new Date(p.updated_at).toLocaleDateString()}</div>
                   <div className="flex items-center"><Archive size={14} className="mr-1"/> {p.revisions?.length || 0} Revisions</div>
                </div>
              </div>
            ))}
          </div>

          {/* Project Details Sidebar */}
          {selectedProject ? (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden h-[600px]">
              <div className="p-5 border-b border-slate-100">
                <h2 className="font-bold text-lg text-slate-800 mb-1">{selectedProject.name || selectedProject.project_id}</h2>
                <p className="text-sm text-slate-500">Active Snapshot: v{selectedProject.active_snapshot_version || selectedProject.graph_version}</p>
                
                <Link href="/editor" className="mt-4 w-full bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded-lg font-medium flex items-center justify-center transition-colors">
                  Open in Editor <ArrowRight size={16} className="ml-2" />
                </Link>
              </div>

              <div className="flex-1 overflow-y-auto p-5 bg-slate-50">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center">
                  <History size={14} className="mr-2" /> Semantic History
                </h3>
                
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-slate-200">
                  {selectedProject.revisions && selectedProject.revisions.length > 0 ? (
                    [...selectedProject.revisions].reverse().map((rev: any, idx: number) => (
                      <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                        <div className="flex items-center justify-center w-5 h-5 rounded-full border border-white bg-indigo-500 text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                          <GitCommit size={10} />
                        </div>
                        <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.25rem)] bg-white p-3 rounded border border-slate-200 shadow-sm">
                          <div className="flex justify-between items-center mb-1">
                            <span className="font-bold text-slate-700 text-sm">v{rev.graph_version}</span>
                            <span className="text-xs text-slate-400">{new Date(rev.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                          </div>
                          <p className="text-xs text-slate-600">{rev.summary}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-slate-400 text-center py-4 relative z-10 bg-slate-50">No revisions yet.</div>
                  )}
                </div>
              </div>
            </div>
          ) : (
             <div className="bg-slate-100 rounded-xl border border-slate-200 flex flex-col items-center justify-center text-slate-400 p-8 h-[600px]">
               <Folder size={48} className="mb-4 text-slate-300" />
               <p className="font-medium text-center">Select a project to view its semantic history</p>
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
