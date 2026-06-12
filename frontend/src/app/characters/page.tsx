"use client";

import { useEffect, useState } from "react";
import { fetchCharacters, generateCharacterConcept, saveCharacter } from "@/lib/api";
import { PlusCircle, Save, Sparkles, UserCircle, MessageSquare, BrainCircuit, Users, Tags } from "lucide-react";

export default function CharacterStudioPage() {
  const [characters, setCharacters] = useState<any[]>([]);
  const [activeChar, setActiveChar] = useState<any | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    try {
      const data = await fetchCharacters();
      setCharacters(data.characters || []);
    } catch (e) {
      console.error(e);
    }
  };

  const createNew = () => {
    setActiveChar({
      id: `char_${Date.now()}`,
      name: "New Character",
      archetype: "hero",
      tags: [],
      voice_profile: { provider: "elevenlabs", profile_id: "default", language: "en" },
      behavior: { talkative: 0.5, aggressive: 0.5, energetic: 0.5, greedy: 0.5, curious: 0.5 },
      speech_style: "neutral",
      appearance: { description: "", concept_images: [], selected_concept: null },
      relationships: []
    });
  };

  const handleSave = async () => {
    if (!activeChar) return;
    await saveCharacter(activeChar);
    await loadCharacters();
  };

  const handleGenerateConcept = async () => {
    if (!activeChar) return;
    setIsGenerating(true);
    try {
      const res = await generateCharacterConcept(activeChar.appearance.description);
      setActiveChar({
        ...activeChar,
        appearance: {
          ...activeChar.appearance,
          concept_images: res.images
        }
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-full bg-slate-50">
      
      {/* Left Sidebar: Character List */}
      <div className="w-80 bg-white border-r border-slate-200 overflow-y-auto flex flex-col">
        <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50 sticky top-0 z-10">
          <h2 className="font-bold text-slate-800">Characters</h2>
          <button onClick={createNew} className="text-blue-600 hover:text-blue-700">
            <PlusCircle size={20} />
          </button>
        </div>
        <div className="p-4 space-y-3">
          {characters.map(c => (
            <div 
              key={c.id} 
              onClick={() => setActiveChar(c)}
              className={`p-3 rounded-lg border cursor-pointer transition-colors flex items-center space-x-3 ${
                activeChar?.id === c.id ? 'bg-blue-50 border-blue-200' : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50'
              }`}
            >
              <div className="w-12 h-12 bg-slate-200 rounded overflow-hidden flex items-center justify-center shrink-0">
                {c.appearance?.selected_concept ? (
                  <img src={c.appearance.selected_concept} alt={c.name} className="w-full h-full object-cover" />
                ) : (
                  <UserCircle size={24} className="text-slate-400" />
                )}
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-slate-800 truncate">{c.name}</h3>
                <p className="text-xs text-slate-500 uppercase tracking-wider">{c.archetype} • {c.speech_style}</p>
              </div>
            </div>
          ))}
          {characters.length === 0 && (
            <p className="text-sm text-slate-400 text-center py-4">No characters yet.</p>
          )}
        </div>
      </div>

      {/* Right Panel: Editor */}
      <div className="flex-1 overflow-y-auto p-8 relative">
        {activeChar ? (
          <div className="max-w-4xl mx-auto space-y-8 pb-20">
            
            {/* Header Actions */}
            <div className="flex justify-between items-start">
              <div>
                <input 
                  type="text" 
                  value={activeChar.name}
                  onChange={e => setActiveChar({...activeChar, name: e.target.value})}
                  className="text-3xl font-bold bg-transparent outline-none border-b border-transparent focus:border-blue-300 text-slate-800 px-1 py-0.5"
                />
                <div className="flex items-center space-x-4 mt-2 px-1 text-slate-500">
                  <span className="text-sm font-mono bg-slate-200 px-2 py-0.5 rounded text-slate-700">{activeChar.id}</span>
                </div>
              </div>
              <button 
                onClick={handleSave}
                className="bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded shadow flex items-center space-x-2"
              >
                <Save size={18} />
                <span>Save Profile</span>
              </button>
            </div>

            {/* Main Editor Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              
              {/* Left Column: Appearance & Voice */}
              <div className="space-y-8">
                
                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <Sparkles size={16} className="mr-2 text-amber-500" />
                    Appearance & Concept
                  </h3>
                  
                  <textarea 
                    placeholder="Describe appearance..."
                    value={activeChar.appearance?.description || ""}
                    onChange={e => setActiveChar({...activeChar, appearance: {...activeChar.appearance, description: e.target.value}})}
                    className="w-full p-3 border border-slate-200 rounded-lg text-sm mb-3 outline-none focus:ring-2 focus:ring-blue-100"
                    rows={3}
                  />
                  <button 
                    onClick={handleGenerateConcept}
                    disabled={isGenerating || !activeChar.appearance?.description}
                    className="w-full bg-blue-50 text-blue-700 font-medium py-2 rounded-lg border border-blue-200 hover:bg-blue-100 disabled:opacity-50 transition-colors flex justify-center items-center"
                  >
                    {isGenerating ? "Generating Concept..." : "Generate Concept"}
                  </button>

                  {/* Concept Images Wrapper */}
                  {activeChar.appearance?.concept_images?.length > 0 && (
                    <div className="mt-4 grid grid-cols-3 gap-2">
                      {activeChar.appearance.concept_images.map((img: string, i: number) => (
                        <div 
                          key={i}
                          onClick={() => setActiveChar({...activeChar, appearance: {...activeChar.appearance, selected_concept: img}})}
                          className={`aspect-square bg-slate-200 rounded overflow-hidden cursor-pointer border-2 transition-all ${
                            activeChar.appearance.selected_concept === img ? "border-blue-500 shadow-md ring-2 ring-blue-200" : "border-transparent"
                          }`}
                        >
                           {/* Mock Image Representation */}
                           <div className="w-full h-full flex flex-col items-center justify-center text-xs text-slate-400 bg-slate-100">
                             <UserCircle size={24} className="mb-1" />
                             Concept {i+1}
                           </div>
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <MessageSquare size={16} className="mr-2 text-indigo-500" />
                    Identity & Voice
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs font-semibold text-slate-500 uppercase">Archetype</label>
                      <input 
                        type="text" 
                        value={activeChar.archetype}
                        onChange={e => setActiveChar({...activeChar, archetype: e.target.value})}
                        className="w-full p-2 border border-slate-200 rounded text-sm mt-1"
                        placeholder="e.g. merchant, hero, policeman"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-slate-500 uppercase">Speech Style</label>
                      <input 
                        type="text" 
                        value={activeChar.speech_style}
                        onChange={e => setActiveChar({...activeChar, speech_style: e.target.value})}
                        className="w-full p-2 border border-slate-200 rounded text-sm mt-1"
                        placeholder="e.g. desi_hinglish"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-slate-500 uppercase">Voice Profile ID</label>
                      <input 
                        type="text" 
                        value={activeChar.voice_profile?.profile_id || ""}
                        onChange={e => setActiveChar({...activeChar, voice_profile: {...activeChar.voice_profile, profile_id: e.target.value}})}
                        className="w-full p-2 border border-slate-200 rounded text-sm mt-1"
                      />
                    </div>
                  </div>
                </section>
                
              </div>

              {/* Right Column: Behavior & Relationships */}
              <div className="space-y-8">
                
                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <BrainCircuit size={16} className="mr-2 text-rose-500" />
                    Behavior Traits
                  </h3>
                  
                  <div className="space-y-4">
                    {["talkative", "aggressive", "energetic", "greedy", "curious"].map(trait => (
                      <div key={trait}>
                        <div className="flex justify-between text-xs font-semibold text-slate-500 uppercase mb-1">
                          <span>{trait}</span>
                          <span>{(activeChar.behavior[trait] * 100).toFixed(0)}%</span>
                        </div>
                        <input 
                          type="range" min="0" max="1" step="0.1"
                          value={activeChar.behavior[trait]}
                          onChange={e => setActiveChar({
                            ...activeChar, 
                            behavior: {...activeChar.behavior, [trait]: parseFloat(e.target.value)}
                          })}
                          className="w-full accent-rose-500"
                        />
                      </div>
                    ))}
                  </div>
                </section>

                <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    <Users size={16} className="mr-2 text-teal-500" />
                    Relationships Graph
                  </h3>
                  
                  <div className="space-y-3">
                    {activeChar.relationships?.map((rel: any, idx: number) => (
                      <div key={idx} className="flex space-x-2 items-center bg-slate-50 p-2 rounded border border-slate-100">
                        <input 
                          type="text" placeholder="Target ID" value={rel.target_id}
                          onChange={e => {
                            const newRels = [...activeChar.relationships];
                            newRels[idx].target_id = e.target.value;
                            setActiveChar({...activeChar, relationships: newRels});
                          }}
                          className="flex-1 p-1 text-sm border border-slate-200 rounded"
                        />
                        <select 
                          value={rel.type}
                          onChange={e => {
                            const newRels = [...activeChar.relationships];
                            newRels[idx].type = e.target.value;
                            setActiveChar({...activeChar, relationships: newRels});
                          }}
                          className="p-1 text-sm border border-slate-200 rounded bg-white"
                        >
                          <option value="friend">Friend</option>
                          <option value="enemy">Enemy</option>
                          <option value="mentor">Mentor</option>
                          <option value="customer">Customer</option>
                        </select>
                      </div>
                    ))}
                    <button 
                      onClick={() => setActiveChar({
                        ...activeChar, 
                        relationships: [...(activeChar.relationships || []), {target_id: "", type: "friend", strength: 0.5}]
                      })}
                      className="text-sm text-teal-600 font-medium hover:underline"
                    >
                      + Add Relationship
                    </button>
                  </div>
                </section>

              </div>
            </div>

          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-400">
            <UserCircle size={64} className="mb-4 text-slate-200" />
            <p>Select a character or create a new one to begin.</p>
          </div>
        )}
      </div>

    </div>
  );
}
