"use client";

import { useState, useEffect } from "react";
import { compileStory, fetchWorlds, fetchCharacters } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { Play, Activity, Globe, Users, FileText, Info, History, Map as MapIcon, ArrowRightLeft, User, MoveRight } from "lucide-react";

export default function EditorPage() {
  const { isDeveloperMode } = useAppStore();
  const [story, setStory] = useState("Halku sells moonlight.\nPoliceman approaches.\nArgument begins.");
  const [semanticData, setSemanticData] = useState<any>(null);
  const [isCompiling, setIsCompiling] = useState(false);
  
  const [worlds, setWorlds] = useState<any[]>([]);
  const [characters, setCharacters] = useState<any[]>([]);
  const [selectedWorld, setSelectedWorld] = useState<string>("");
  const [selectedChars, setSelectedChars] = useState<string[]>([]);
  
  // Preview State
  const [activeBeatId, setActiveBeatId] = useState<string | null>(null);
  const [explainTab, setExplainTab] = useState<"current"|"entire">("current");

  useEffect(() => {
    fetchWorlds().then(d => setWorlds(d.worlds || [])).catch(() => {});
    fetchCharacters().then(d => setCharacters(d.characters || [])).catch(() => {});
  }, []);

  const handleCompile = async () => {
    setIsCompiling(true);
    try {
      const data = await compileStory({
        text: story,
        world_id: selectedWorld,
        characters: selectedChars
      });
      setSemanticData(data);
      if (data.beats && data.beats.length > 0) {
        setActiveBeatId(data.beats[0].id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsCompiling(false);
    }
  };

  const getActiveBeat = () => {
    if (!semanticData || !semanticData.beats || !activeBeatId) return null;
    return semanticData.beats.find((b: any) => b.id === activeBeatId);
  };

  const activeBeat = getActiveBeat();

  return (
    <div className="flex h-full bg-slate-50 relative">
      
      {/* Pane 1: Story Input */}
      <div className="w-[350px] bg-white border-r border-slate-200 flex flex-col p-4 shadow-sm z-10">
        <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center">
          <FileText size={16} className="mr-2 text-indigo-500" />
          Story Script
        </h2>
        
        <div className="space-y-3 mb-4">
           <div className="bg-slate-50 p-2 rounded border border-slate-200 flex items-center space-x-2">
             <Globe size={16} className="text-indigo-500 shrink-0" />
             <select className="flex-1 outline-none text-xs bg-transparent font-medium text-slate-700" value={selectedWorld} onChange={e => setSelectedWorld(e.target.value)}>
               <option value="">No World Selected</option>
               {worlds.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
             </select>
           </div>
           <div className="bg-slate-50 p-2 rounded border border-slate-200 flex flex-col space-y-2">
             <div className="flex items-center space-x-2">
               <Users size={16} className="text-teal-500 shrink-0" />
               <select className="flex-1 outline-none text-xs bg-transparent font-medium text-slate-700" onChange={e => {if(e.target.value && !selectedChars.includes(e.target.value)) setSelectedChars([...selectedChars, e.target.value])}}>
                 <option value="">Add Character...</option>
                 {characters.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
               </select>
             </div>
             {selectedChars.length > 0 && (
               <div className="flex flex-wrap gap-1 mt-1">
                 {selectedChars.map(cId => {
                    const c = characters.find(x => x.id === cId);
                    return (
                      <span key={cId} className="bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full text-[10px] font-medium border border-teal-100 flex items-center">
                        {c?.name || cId}
                        <button className="ml-1 text-teal-400 hover:text-teal-600" onClick={() => setSelectedChars(selectedChars.filter(id => id !== cId))}>×</button>
                      </span>
                    )
                 })}
               </div>
             )}
           </div>
        </div>

        <div className="flex-1 bg-slate-50 rounded border border-slate-200 flex flex-col">
          <textarea
            className="flex-1 w-full p-3 resize-none outline-none text-slate-700 text-sm leading-relaxed bg-transparent"
            value={story}
            onChange={(e) => setStory(e.target.value)}
            placeholder="Write your story here..."
          />
        </div>

        <button 
          onClick={handleCompile}
          disabled={isCompiling}
          className="mt-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white px-4 py-3 rounded shadow flex justify-center items-center space-x-2 font-medium"
        >
          <Activity size={18} />
          <span>{isCompiling ? "Simulating..." : "Simulate Preview"}</span>
        </button>
      </div>

      {/* Pane 2: Semantic Simulator Canvas & Timeline */}
      <div className="flex-1 flex flex-col bg-slate-100 relative">
        
        {/* Canvas Area */}
        <div className="flex-1 flex items-center justify-center p-8 relative overflow-hidden">
          {activeBeat ? (
            <div className="flex flex-col items-center max-w-2xl w-full">
              
              {/* Dialogue Bubble */}
              {activeBeat.dialogue && (
                <div className="bg-white px-6 py-4 rounded-xl shadow-lg border border-slate-200 mb-8 max-w-lg relative">
                  <p className="text-slate-800 text-lg italic text-center font-serif">"{activeBeat.dialogue}"</p>
                  <div className="absolute -bottom-2 left-1/2 -ml-2 w-4 h-4 bg-white border-b border-r border-slate-200 transform rotate-45"></div>
                </div>
              )}

              {/* Formation Visual */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 w-full flex items-center justify-center space-x-12">
                {activeBeat.formation_visual === "face_to_face" && (
                  <>
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 bg-blue-100 text-blue-500 rounded-full flex items-center justify-center border-4 border-blue-50 mb-2 shadow-sm"><User size={32}/></div>
                      <span className="text-xs font-bold text-slate-500 uppercase">Actor 1</span>
                    </div>
                    <ArrowRightLeft size={32} className="text-slate-300" />
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 bg-rose-100 text-rose-500 rounded-full flex items-center justify-center border-4 border-rose-50 mb-2 shadow-sm"><User size={32}/></div>
                      <span className="text-xs font-bold text-slate-500 uppercase">Actor 2</span>
                    </div>
                  </>
                )}
                {activeBeat.formation_visual === "pursuit" && (
                  <>
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 bg-rose-100 text-rose-500 rounded-full flex items-center justify-center border-4 border-rose-50 mb-2 shadow-sm"><User size={32}/></div>
                      <span className="text-xs font-bold text-slate-500 uppercase">Target</span>
                    </div>
                    <MoveRight size={32} className="text-slate-300" />
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 bg-blue-100 text-blue-500 rounded-full flex items-center justify-center border-4 border-blue-50 mb-2 shadow-sm"><User size={32}/></div>
                      <span className="text-xs font-bold text-slate-500 uppercase">Actor</span>
                    </div>
                  </>
                )}
                {activeBeat.formation_visual === "side_by_side" && (
                  <>
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 bg-blue-100 text-blue-500 rounded-full flex items-center justify-center border-4 border-blue-50 mb-2 shadow-sm"><User size={32}/></div>
                      <span className="text-xs font-bold text-slate-500 uppercase">Actor 1</span>
                    </div>
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 bg-teal-100 text-teal-500 rounded-full flex items-center justify-center border-4 border-teal-50 mb-2 shadow-sm"><User size={32}/></div>
                      <span className="text-xs font-bold text-slate-500 uppercase">Actor 2</span>
                    </div>
                  </>
                )}
                {/* Fallback layout */}
                {["face_to_face", "pursuit", "side_by_side"].indexOf(activeBeat.formation_visual) === -1 && (
                  <div className="text-slate-400 font-mono text-sm">Formation: {activeBeat.formation_visual}</div>
                )}
              </div>
              
              <div className="mt-6 flex space-x-4">
                <div className="bg-slate-200 text-slate-600 px-3 py-1 rounded text-xs font-bold uppercase tracking-wider">
                  Intent: {activeBeat.intent}
                </div>
                <div className="bg-slate-200 text-slate-600 px-3 py-1 rounded text-xs font-bold uppercase tracking-wider">
                  Formation: {activeBeat.formation_id}
                </div>
              </div>

            </div>
          ) : (
            <div className="text-slate-400 text-center flex flex-col items-center">
              <Play size={48} className="mb-4 text-slate-300" />
              <p>Simulate the story to preview execution.</p>
            </div>
          )}
        </div>

        {/* Timeline Scrubber */}
        {semanticData?.beats && (
          <div className="h-40 bg-white border-t border-slate-200 p-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-20">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Execution Timeline</h3>
            <div className="flex space-x-2 overflow-x-auto pb-2">
              {semanticData.beats.map((beat: any, idx: number) => (
                <div 
                  key={beat.id}
                  onClick={() => setActiveBeatId(beat.id)}
                  className={`min-w-[150px] p-3 rounded border cursor-pointer transition-colors ${
                    activeBeatId === beat.id ? 'bg-indigo-50 border-indigo-300 ring-1 ring-indigo-200 shadow-sm' : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="text-[10px] text-slate-400 font-bold uppercase mb-1">Beat {idx + 1} • {beat.time}s</div>
                  <div className="text-xs font-bold text-slate-700 truncate">{beat.intent}</div>
                  <div className="text-[10px] text-slate-500 truncate mt-1">{beat.formation_id}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Pane 3: Explainability & Map */}
      <div className="w-[300px] bg-white border-l border-slate-200 flex flex-col shadow-sm z-10 overflow-y-auto">
        
        {/* Tabs */}
        <div className="flex border-b border-slate-100">
          <button 
            onClick={() => setExplainTab("current")}
            className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors ${explainTab === "current" ? "border-indigo-500 text-indigo-600" : "border-transparent text-slate-400 hover:text-slate-600"}`}
          >
            Current Beat
          </button>
          <button 
            onClick={() => setExplainTab("entire")}
            className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors ${explainTab === "entire" ? "border-indigo-500 text-indigo-600" : "border-transparent text-slate-400 hover:text-slate-600"}`}
          >
            Entire Story
          </button>
        </div>

        {/* Explain Content */}
        <div className="p-4 space-y-6">
          
          {explainTab === "current" && activeBeat && (
            <>
              <div>
                <h3 className="text-sm font-bold text-slate-800 mb-2 flex items-center">
                  <Info size={14} className="mr-2 text-blue-500" /> Reasoning
                </h3>
                <ul className="space-y-2">
                  {activeBeat.explanation.map((exp: string, i: number) => (
                    <li key={i} className="text-xs text-slate-600 flex items-start">
                      <span className="text-blue-400 mr-2">•</span> {exp}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-800 mb-2 flex items-center">
                  <MapIcon size={14} className="mr-2 text-emerald-500" /> Active Path
                </h3>
                <div className="bg-slate-50 p-3 rounded border border-slate-200">
                  {activeBeat.state_snapshot.active_path.map((zone: string, i: number, arr: any[]) => (
                    <div key={i} className="flex flex-col">
                      <span className={`text-xs font-medium px-2 py-1 rounded ${
                        zone === activeBeat.state_snapshot.active_zone ? "bg-emerald-100 text-emerald-800" : "bg-white text-slate-500 border border-slate-200"
                      }`}>
                        {zone}
                      </span>
                      {i < arr.length - 1 && <div className="text-slate-300 text-[10px] pl-4 py-1">↓</div>}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {explainTab === "entire" && semanticData?.beats && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-800 flex items-center">
                <History size={14} className="mr-2 text-slate-500" /> Story Log
              </h3>
              {semanticData.beats.map((b: any, i: number) => (
                <div key={b.id} className="border-l-2 border-slate-200 pl-3 pb-2">
                  <div className="text-xs font-bold text-slate-700 mb-1">Beat {i + 1}: {b.intent}</div>
                  <div className="text-[10px] text-slate-500 space-y-1">
                    {b.explanation.map((exp: string, j: number) => (
                      <div key={j}>• {exp}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {!activeBeat && (
            <p className="text-xs text-slate-400 text-center py-4 italic">Compile story to view engine reasoning.</p>
          )}

        </div>
      </div>

    </div>
  );
}
