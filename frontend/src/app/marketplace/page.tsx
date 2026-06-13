"use client";

import { useState, useEffect } from "react";
import { fetchMarketplaceAssets, forkMarketplaceAsset, rateMarketplaceAsset, downloadMarketplaceAsset, fetchMockUsers } from "@/lib/api";
import { Search, Filter, Star, Download, GitFork, ShieldCheck, HardDriveDownload, UserCircle } from "lucide-react";

export default function MarketplaceDashboard() {
  const [assets, setAssets] = useState<any[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<any>(null);
  const [mockUsers, setMockUsers] = useState<any[]>([]);
  const [activeUser, setActiveUser] = useState<any>(null);
  const [filterType, setFilterType] = useState<string>("");

  useEffect(() => {
    loadAssets();
    fetchMockUsers().then(res => {
      const users = res.users || [];
      setMockUsers(users);
      if (users.length > 0) setActiveUser(users[0]);
    });
  }, [filterType]);

  const loadAssets = () => {
    const q = filterType ? `?type=${filterType}` : "";
    fetchMarketplaceAssets(q).then(res => setAssets(res.assets || []));
  };

  const handleFork = async (assetId: string) => {
    if (!activeUser) return;
    await forkMarketplaceAsset(assetId, activeUser.user_id);
    loadAssets();
  };

  const handleRate = async (assetId: string, score: number) => {
    if (!activeUser) return;
    await rateMarketplaceAsset(assetId, activeUser.user_id, score);
    loadAssets();
    if (selectedAsset?.asset_id === assetId) {
      setSelectedAsset({...selectedAsset, rating: score});
    }
  };

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Filters Sidebar */}
      <div className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-4 border-b border-slate-200">
          <h2 className="font-bold text-slate-800 flex items-center">
            <Filter className="mr-2 text-indigo-500" size={18} /> Filters
          </h2>
        </div>
        <div className="p-4 flex-1 overflow-y-auto">
          <div className="mb-6">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Asset Type</h3>
            <div className="space-y-2">
              {['character', 'world', 'template', 'story_graph', 'formation'].map(t => (
                <label key={t} className="flex items-center space-x-2 text-sm text-slate-600">
                  <input 
                    type="radio" 
                    name="type" 
                    value={t} 
                    checked={filterType === t}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="text-indigo-600"
                  />
                  <span className="capitalize">{t.replace('_', ' ')}</span>
                </label>
              ))}
              <label className="flex items-center space-x-2 text-sm text-slate-600">
                  <input 
                    type="radio" 
                    name="type" 
                    value="" 
                    checked={filterType === ""}
                    onChange={() => setFilterType("")}
                    className="text-indigo-600"
                  />
                  <span>All Types</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-6 border-b border-slate-200 bg-white flex justify-between items-center shadow-sm z-10">
          <div className="flex-1 max-w-xl relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search Semantic Assets..." 
              className="w-full pl-10 pr-4 py-2 bg-slate-100 border-none rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          
          <div className="ml-4 flex items-center">
             {activeUser && (
              <div className="flex items-center bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 shadow-sm">
                <UserCircle size={16} className="text-slate-400 mr-2" />
                <span className="text-sm font-medium text-slate-600 mr-2">Acting As:</span>
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
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {assets.length === 0 ? (
              <div className="col-span-full py-12 text-center text-slate-500 bg-white border border-dashed rounded-xl border-slate-300">
                No assets found.
              </div>
            ) : assets.map((asset) => (
              <div 
                key={asset.asset_id}
                onClick={() => setSelectedAsset(asset)}
                className={`bg-white border rounded-xl p-5 shadow-sm cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md ${selectedAsset?.asset_id === asset.asset_id ? 'border-indigo-500 ring-2 ring-indigo-50' : 'border-slate-200'}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-slate-800 line-clamp-1">{asset.title}</h3>
                  {asset.featured && <span className="bg-amber-100 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded-full">FEATURED</span>}
                </div>
                <div className="text-xs text-indigo-500 uppercase font-semibold mb-3 tracking-wide">{asset.asset_type.replace('_', ' ')}</div>
                
                <p className="text-sm text-slate-500 mb-4 line-clamp-2 h-10">{asset.description}</p>
                
                <div className="flex items-center justify-between text-xs text-slate-500 font-medium pt-3 border-t border-slate-100">
                  <div className="flex items-center text-amber-500">
                    <Star size={14} className="mr-1 fill-amber-500" />
                    {asset.rating.toFixed(1)} ({asset.rating_count})
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="flex items-center"><Download size={12} className="mr-1" /> {asset.downloads}</span>
                    <span className="flex items-center"><GitFork size={12} className="mr-1" /> {asset.forks}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Asset Inspector */}
      {selectedAsset && (
        <div className="w-80 bg-white border-l border-slate-200 flex flex-col shadow-xl z-20">
          <div className="p-5 border-b border-slate-100 bg-slate-50 relative">
            <h2 className="font-bold text-lg text-slate-800">{selectedAsset.title}</h2>
            <p className="text-sm text-slate-500 mb-4">v{selectedAsset.versions[selectedAsset.versions.length - 1]?.version} • By {selectedAsset.author_id}</p>
            
            <div className="flex space-x-2">
              <button 
                onClick={() => handleFork(selectedAsset.asset_id)}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg text-sm font-medium flex justify-center items-center transition-colors"
              >
                <GitFork size={16} className="mr-2" /> Fork Asset
              </button>
            </div>
            <button className="absolute top-4 right-4 text-slate-400 hover:text-slate-600" onClick={() => setSelectedAsset(null)}>✕</button>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center">
                <ShieldCheck size={14} className="mr-1" /> Asset Health
              </h3>
              <div className="flex items-center">
                <div className="flex-1 bg-slate-100 rounded-full h-2 mr-3">
                  <div className={`h-2 rounded-full ${selectedAsset.health_score > 80 ? 'bg-emerald-500' : selectedAsset.health_score > 50 ? 'bg-amber-500' : 'bg-rose-500'}`} style={{width: `${selectedAsset.health_score}%`}}></div>
                </div>
                <span className="text-sm font-bold text-slate-700">{selectedAsset.health_score}/100</span>
              </div>
            </div>

            {selectedAsset.required_assets?.length > 0 && (
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center">
                  <HardDriveDownload size={14} className="mr-1" /> Dependencies
                </h3>
                <ul className="space-y-1">
                  {selectedAsset.required_assets.map((dep: string) => (
                    <li key={dep} className="text-sm text-slate-600 bg-slate-50 px-2 py-1 rounded border border-slate-100">{dep}</li>
                  ))}
                </ul>
              </div>
            )}

            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Rate Asset</h3>
              <div className="flex space-x-1">
                {[1,2,3,4,5].map(s => (
                  <button 
                    key={s} 
                    onClick={() => handleRate(selectedAsset.asset_id, s)}
                    className="text-slate-300 hover:text-amber-500 transition-colors"
                  >
                    <Star size={24} className={selectedAsset.rating >= s ? 'fill-amber-500 text-amber-500' : ''} />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Version History</h3>
              <div className="space-y-3 relative before:absolute before:inset-0 before:ml-2 before:h-full before:w-0.5 before:bg-slate-200">
                {[...selectedAsset.versions].reverse().map((v: any, idx: number) => (
                  <div key={idx} className="relative flex items-start group">
                    <div className="flex items-center justify-center w-4 h-4 mt-0.5 rounded-full border border-white bg-indigo-500 text-white shadow z-10"></div>
                    <div className="ml-3 bg-slate-50 p-2 rounded text-sm w-full border border-slate-100">
                      <div className="font-bold text-slate-700">v{v.version}</div>
                      <div className="text-slate-500 text-xs">{v.summary}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
          </div>
        </div>
      )}
    </div>
  );
}
