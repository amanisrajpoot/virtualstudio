import Link from "next/link";
import { Film, LayoutDashboard, PenTool, Globe, Server, Users, Activity, Folder } from "lucide-react";

export function Sidebar() {
  return (
    <div className="w-64 bg-slate-900 text-slate-300 flex flex-col h-screen border-r border-slate-800">
      <div className="p-4 border-b border-slate-800">
        <h1 className="text-xl font-bold text-white">StoryForge</h1>
        <p className="text-xs text-slate-500">Creator Dashboard</p>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        <Link href="/" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 text-white">
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </Link>
        <Link href="/projects" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 text-white">
          <Folder size={20} />
          <span>Projects</span>
        </Link>
        <Link href="/editor" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <PenTool size={20} />
          <span>Story Editor</span>
        </Link>
        <Link href="/story-graph" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <Activity size={20} />
          <span>Semantic Graph</span>
        </Link>
        <div className="pt-4 pb-2 text-xs uppercase text-slate-500 font-semibold">Ecosystem</div>
        <Link href="/marketplace" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <Globe size={20} />
          <span>Marketplace</span>
        </Link>
        <div className="pt-4 pb-2 text-xs uppercase text-slate-500 font-semibold">Studios</div>
        <Link href="/characters" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <Users size={20} />
          <span>Characters</span>
        </Link>
        <Link href="/worlds" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <Globe size={20} />
          <span>Worlds</span>
        </Link>
        <div className="pt-4 pb-2 text-xs uppercase text-slate-500 font-semibold">Render</div>
        <Link href="/queue" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <Server size={20} />
          <span>Render Queue</span>
        </Link>
        <Link href="/library" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <Film size={20} />
          <span>Video Library</span>
        </Link>
        <div className="pt-4 pb-2 text-xs uppercase text-slate-500 font-semibold">Developer</div>
        <Link href="/diagnostics" className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 hover:text-white">
          <Activity size={20} />
          <span>Diagnostics</span>
        </Link>
      </nav>
    </div>
  );
}
