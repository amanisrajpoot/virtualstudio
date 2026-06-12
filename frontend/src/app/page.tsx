"use client";

import { useEffect, useState } from "react";
import { fetchProjects } from "@/lib/api";
import Link from "next/link";
import { PlusCircle, MoreVertical } from "lucide-react";

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    fetchProjects().then(data => setProjects(data.projects)).catch(() => {});
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-slate-800">Your Projects</h1>
        <Link href="/editor" className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          <PlusCircle size={18} />
          <span>New Story</span>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {projects.map((p: any) => (
          <div key={p.id} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-semibold text-lg text-slate-800">{p.name}</h3>
              <button className="text-slate-400 hover:text-slate-600">
                <MoreVertical size={18} />
              </button>
            </div>
            <div className="flex items-center justify-between mt-6">
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                p.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
              }`}>
                {p.status}
              </span>
              <Link href="/editor" className="text-sm text-blue-600 font-medium hover:underline">
                Open Workspace
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
