"use client";

import { PlayCircle, Clock, Users, MapPin } from "lucide-react";

export default function LibraryPage() {
  const videos = [
    {
      id: "v1",
      title: "Moonlight Seller",
      duration: "28s",
      characters: ["Halku", "Police"],
      world: "Village Market",
      thumbnail: "bg-slate-200"
    },
    {
      id: "v2",
      title: "The Tea Stall Gossip",
      duration: "45s",
      characters: ["Ramesh", "Suresh"],
      world: "Delhi Street",
      thumbnail: "bg-slate-300"
    }
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto h-full overflow-auto bg-slate-50">
      <h1 className="text-2xl font-bold text-slate-800 mb-8">Video Library</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map(v => (
          <div key={v.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden group">
            <div className={`h-40 ${v.thumbnail} relative flex items-center justify-center`}>
              <PlayCircle size={48} className="text-white opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer drop-shadow-md" />
              <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded font-medium flex items-center">
                <Clock size={12} className="mr-1" />
                {v.duration}
              </div>
            </div>
            
            <div className="p-4">
              <h3 className="font-bold text-lg text-slate-800 mb-3">{v.title}</h3>
              
              <div className="space-y-2">
                <div className="flex items-start text-sm text-slate-600">
                  <Users size={16} className="mr-2 mt-0.5 text-slate-400" />
                  <div className="flex flex-wrap gap-1">
                    {v.characters.map(c => (
                      <span key={c} className="bg-slate-100 px-2 py-0.5 rounded text-xs font-medium">{c}</span>
                    ))}
                  </div>
                </div>
                
                <div className="flex items-center text-sm text-slate-600">
                  <MapPin size={16} className="mr-2 text-slate-400" />
                  <span className="bg-amber-50 text-amber-700 px-2 py-0.5 rounded text-xs font-medium border border-amber-100">
                    {v.world}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
