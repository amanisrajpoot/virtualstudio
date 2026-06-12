"use client";

import { useAppStore } from "@/lib/store";
import { Terminal } from "lucide-react";

export function Header() {
  const { isDeveloperMode, toggleDeveloperMode } = useAppStore();

  return (
    <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6">
      <div className="font-medium text-slate-800">Workspace</div>
      
      <button 
        onClick={toggleDeveloperMode}
        className={`flex items-center space-x-2 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
          isDeveloperMode 
            ? "bg-slate-800 text-green-400" 
            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
        }`}
      >
        <Terminal size={16} />
        <span>Developer Mode</span>
      </button>
    </header>
  );
}
