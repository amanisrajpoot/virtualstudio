"use client";

import { useEffect, useState } from "react";
import { fetchWorlds, saveWorld, generateWorld } from "@/lib/api";
import { PlusCircle, Save, Globe, Network, Map, LayoutTemplate, Activity } from "lucide-react";

export default function WorldStudioPage() {
  const [worlds, setWorlds] = useState<any[]>([]);
  const [activeWorld, setActiveWorld] = useState<any | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    loadWorlds();
  }, []);

  const loadWorlds = async () => {
    try {
      const data = await fetchWorlds();
      setWorlds(data.worlds || []);
    } catch (e) {
      console.error(e);
    }
  };

  const createNew = () => {
    setActiveWorld({
      id: `world_${Date.now()}`,
      name: "New World",
      archetype: "commercial",
      description: "",
      zones: [],
      formations: [],
      props: [],
      ambience: { time_of_day: "day", weather: "clear", crowd_density: 0.5, noise_profile: "ambient" },
      connected_worlds: []
    });
  };

  const handleSave = async () => {
    if (!activeWorld) return;
    await saveWorld(activeWorld);
    await loadWorlds();
  };

  const handleGenerate = async () => {
    if (!activeWorld) return;
    setIsGenerating(true);
    try {
      const res = await generateWorld(activeWorld.description);
      setActiveWorld({
        ...activeWorld,
        zones: res.zones,
        props: res.props
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-full bg-slate-50">
      
      {/* Left Sidebar: World List */}
      <div className="w-80 bg-white border-r border-slate-200 overflow-y-auto flex flex-col">
        <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50 sticky top-0 z-10">
          <h2 className="font-bold text-slate-800">Worlds</h2>
          <button onClick={createNew} className="text-blue-600 hover:text-blue-700">
            <PlusCircle size={20} />
          </button>
        </div>
        <div className="p-4 space-y-3">
          {worlds.map(w => (
            <div 
              key={w.id} 
              onClick={() => setActiveWorld(w)}
              className={`p-3 rounded-lg border cursor-pointer transition-colors flex items-center space-x-3 ${
                activeWorld?.id === w.id ? 'bg-indigo-50 border-indigo-200' : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50'
              }`}
            >
              <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center shrink-0 border border-slate-200 text-indigo-500">
                <Globe size={20} />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-slate-800 truncate">{w.name}</h3>
                <p className="text-xs text-slate-500 uppercase tracking-wider">{w.archetype}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel: Editor */}
      <div className="flex-1 overflow-y-auto p-8 relative">
        {activeWorld ? (
          <div className="max-w-5xl mx-auto space-y-8 pb-20">
            
            {/* Header Actions */}
            <div className="flex justify-between items-start">
              <div className="flex-1 mr-8">
                <input 
                  type="text" 
                  value={activeWorld.name}
                  onChange={e => setActiveWorld({...activeWorld, name: e.target.value})}
                  className="text-3xl w-full font-bold bg-transparent outline-none border-b border-transparent focus:border-indigo-300 text-slate-800 px-1 py-0.5"
                />
                <div className="flex items-center space-x-4 mt-2 px-1 text-slate-500">
                  <span className="text-sm font-mono bg-slate-200 px-2 py-0.5 rounded text-slate-700">{activeWorld.id}</span>
                </div>
              </div>
              <button 
                onClick={handleSave}
                className="bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded shadow flex items-center space-x-2 shrink-0"
              >
                <Save size={18} />
                <span>Save World</span>
              </button>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
              
              {/* Main Column: Definition & Generation */}
              <div className="xl:col-span-2 space-y-8">
                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <LayoutTemplate size={16} className="mr-2 text-indigo-500" />
                    Identity & Generation
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs font-semibold text-slate-500 uppercase">Archetype</label>
                      <input 
                        type="text" 
                        value={activeWorld.archetype}
                        onChange={e => setActiveWorld({...activeWorld, archetype: e.target.value})}
                        className="w-full p-2 border border-slate-200 rounded text-sm mt-1"
                        placeholder="e.g. commercial, residential, institutional"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-slate-500 uppercase">Description / Prompt</label>
                      <textarea 
                        value={activeWorld.description}
                        onChange={e => setActiveWorld({...activeWorld, description: e.target.value})}
                        className="w-full p-3 border border-slate-200 rounded-lg text-sm mt-1 outline-none focus:ring-2 focus:ring-indigo-100"
                        rows={3}
                        placeholder="Describe the world to automatically generate zones and props..."
                      />
                    </div>
                    <button 
                      onClick={handleGenerate}
                      disabled={isGenerating || !activeWorld.description}
                      className="w-full bg-indigo-50 text-indigo-700 font-medium py-2 rounded-lg border border-indigo-200 hover:bg-indigo-100 disabled:opacity-50 transition-colors flex justify-center items-center"
                    >
                      {isGenerating ? "Generating Zones & Props..." : "Generate World Structure"}
                    </button>
                  </div>
                </section>

                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <Map size={16} className="mr-2 text-emerald-500" />
                    Zone Graph Preview
                  </h3>
                  
                  {activeWorld.zones?.length > 0 ? (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 overflow-x-auto">
                      <div className="flex flex-wrap gap-4 items-center justify-center">
                        {activeWorld.zones.map((zone: any) => (
                           <div key={zone.id} className="flex flex-col items-center">
                             <div className="bg-white border-2 border-emerald-200 p-3 rounded-lg shadow-sm w-32 text-center relative">
                               <div className="text-xs font-bold text-slate-700 truncate">{zone.name}</div>
                               <div className="text-[10px] text-slate-400 uppercase mt-1">{zone.zone_type}</div>
                               {zone.capacity > 0 && <div className="absolute -top-2 -right-2 bg-emerald-100 text-emerald-700 text-[10px] font-bold px-1.5 py-0.5 rounded-full border border-emerald-200">{zone.capacity}</div>}
                             </div>
                             {zone.adjacent?.length > 0 && (
                               <div className="text-xs text-slate-400 mt-2">→ {zone.adjacent.join(", ")}</div>
                             )}
                           </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-8 text-center text-slate-400 text-sm">
                      Generate the world to view the zone graph.
                    </div>
                  )}
                </section>
              </div>

              {/* Sidebar Column: Atmosphere, Props, Connections */}
              <div className="space-y-8">
                
                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <Activity size={16} className="mr-2 text-sky-500" />
                    Atmosphere
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold text-slate-500 uppercase">Time</span>
                      <select className="p-1 text-sm border border-slate-200 rounded bg-white" value={activeWorld.ambience?.time_of_day} onChange={e => setActiveWorld({...activeWorld, ambience: {...activeWorld.ambience, time_of_day: e.target.value}})}>
                        <option value="day">Day</option>
                        <option value="night">Night</option>
                        <option value="morning">Morning</option>
                        <option value="evening">Evening</option>
                      </select>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold text-slate-500 uppercase">Weather</span>
                      <select className="p-1 text-sm border border-slate-200 rounded bg-white" value={activeWorld.ambience?.weather} onChange={e => setActiveWorld({...activeWorld, ambience: {...activeWorld.ambience, weather: e.target.value}})}>
                        <option value="clear">Clear</option>
                        <option value="rain">Rain</option>
                        <option value="cloudy">Cloudy</option>
                      </select>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-semibold text-slate-500 uppercase mb-1">
                        <span>Crowd Density</span>
                        <span>{Math.round(activeWorld.ambience?.crowd_density * 100)}%</span>
                      </div>
                      <input 
                        type="range" min="0" max="1" step="0.1" 
                        value={activeWorld.ambience?.crowd_density}
                        onChange={e => setActiveWorld({...activeWorld, ambience: {...activeWorld.ambience, crowd_density: parseFloat(e.target.value)}})}
                        className="w-full accent-sky-500"
                      />
                    </div>
                  </div>
                </section>

                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <Network size={16} className="mr-2 text-rose-500" />
                    Connections & Props
                  </h3>
                  
                  <div className="mb-4">
                    <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Connected Worlds</h4>
                    <div className="space-y-2">
                      {activeWorld.connected_worlds?.map((conn: any, i: number) => (
                        <div key={i} className="text-sm bg-slate-50 p-2 rounded border border-slate-100 flex justify-between items-center">
                          <span className="font-medium text-slate-700">{conn.target_world}</span>
                          <span className="text-xs text-slate-400">{conn.connection_type}</span>
                        </div>
                      ))}
                      {(!activeWorld.connected_worlds || activeWorld.connected_worlds.length === 0) && (
                        <p className="text-xs text-slate-400 italic">No connected worlds.</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Required Props</h4>
                    <div className="flex flex-wrap gap-2">
                      {activeWorld.props?.map((prop: any, i: number) => (
                        <span key={i} className={`px-2 py-1 rounded text-xs font-medium border ${prop.required ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                          {prop.prop_id}
                        </span>
                      ))}
                      {(!activeWorld.props || activeWorld.props.length === 0) && (
                        <p className="text-xs text-slate-400 italic">No props defined.</p>
                      )}
                    </div>
                  </div>
                </section>

              </div>
            </div>

          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-400">
            <Globe size={64} className="mb-4 text-slate-200" />
            <p>Select a world template or create a new one to begin.</p>
          </div>
        )}
      </div>

    </div>
  );
}
