"use client";

import { useState, useCallback, useEffect } from "react";
import ReactFlow, { Background, Controls, Node, Edge, Position, useNodesState, useEdgesState } from "reactflow";
import "reactflow/dist/style.css";
import { fetchStoryGraph, overrideStoryIntent } from "@/lib/api";
import { AlertTriangle, Lock, RefreshCw, Activity, ArrowRight, Settings2 } from "lucide-react";

// MOCK CONSTANTS FOR DEMO
const DEMO_STORY_ID = "test_story_1";
const DEMO_TEXT = "Halku sets up a stall. The policeman approaches. They argue.";
const DEMO_WORLD = "village_market";
const DEMO_CHARS = ["halku", "policeman"];

const CustomBeatNode = ({ data }: any) => {
  const isOverridden = data.status === "overridden";
  const isDirty = data.status === "dirty";
  const isLowConfidence = data.confidence < 80;
  
  return (
    <div className={`bg-white rounded-lg border-2 p-4 w-64 shadow-sm relative transition-colors duration-300 ${
      isDirty ? 'border-orange-500 bg-orange-50' :
      isOverridden ? 'border-blue-500' : 
      isLowConfidence ? 'border-amber-400' : 'border-slate-200'
    }`}>
      {isDirty && (
        <div className="absolute -top-3 right-2 bg-orange-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center shadow-sm">
          <Activity size={10} className="mr-1"/> DIRTY
        </div>
      )}
      {isOverridden && !isDirty && (
        <div className="absolute -top-3 right-2 bg-blue-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center shadow-sm">
          <RefreshCw size={10} className="mr-1"/> OVERRIDDEN
        </div>
      )}
      {data.status === "locked" && (
        <div className="absolute -top-3 right-2 bg-slate-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center shadow-sm">
          <Lock size={10} className="mr-1"/> LOCKED
        </div>
      )}
      
      <div className="text-[10px] font-bold text-slate-400 uppercase mb-1 flex justify-between">
        <span>{data.beat_type}</span>
        <span className={isLowConfidence ? "text-amber-500" : ""}>{data.confidence}% Conf</span>
      </div>
      <div className="text-lg font-bold text-slate-800">{data.intent}</div>
      <div className="mt-2 text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-100">
        Zone: {data.zone || "Any"} <br/>
        Formation: {data.formation || "Any"}
      </div>
    </div>
  );
};

const nodeTypes = {
  beatNode: CustomBeatNode,
};

export default function StoryGraphPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [graphData, setGraphData] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  
  // Override Inspector State
  const [newIntent, setNewIntent] = useState("");

  const loadGraph = async () => {
    try {
      const data = await fetchStoryGraph({
        story_id: DEMO_STORY_ID,
        text: DEMO_TEXT,
        world_id: DEMO_WORLD,
        characters: DEMO_CHARS
      });
      setGraphData(data);
      
      // Transform backend nodes to ReactFlow nodes
      const rfNodes: Node[] = [];
      const rfEdges: Edge[] = [];
      
      data.nodes.forEach((n: any, idx: number) => {
        rfNodes.push({
          id: n.id,
          type: "beatNode",
          position: { x: 250, y: 100 + (idx * 200) },
          data: n,
        });
        
        n.next_nodes.forEach((nextId: str) => {
          rfEdges.push({
            id: `${n.id}-${nextId}`,
            source: n.id,
            target: nextId,
            animated: true,
            style: { stroke: '#94a3b8', strokeWidth: 2 }
          });
        });
      });
      
      setNodes(rfNodes);
      setEdges(rfEdges);
      if(selectedNode) {
         const updatedSelected = rfNodes.find(x => x.id === selectedNode.id);
         setSelectedNode(updatedSelected || null);
      }
    } catch(e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  const onNodeClick = (event: any, node: Node) => {
    setSelectedNode(node);
    setNewIntent(node.data.intent);
  };

  const handleOverride = async () => {
    if (!selectedNode || !newIntent) return;
    try {
      await overrideStoryIntent({
        story_id: DEMO_STORY_ID,
        node_id: selectedNode.id,
        original_intent: selectedNode.data.intent,
        overridden_intent: newIntent
      });
      await loadGraph(); // Refresh entire graph
    } catch(e) {
      console.error(e);
    }
  };

  return (
    <div className="flex h-full bg-slate-50 relative">
      <div className="flex-1 relative">
         <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background color="#cbd5e1" gap={20} size={1} />
          <Controls />
        </ReactFlow>
        
        {graphData && (
          <div className="absolute top-4 left-4 bg-white p-3 rounded-lg shadow-sm border border-slate-200 z-10 flex items-center space-x-4">
             <div>
               <div className="text-[10px] font-bold text-slate-400 uppercase">Graph Version</div>
               <div className="text-sm font-bold text-slate-700">v{graphData.version}</div>
             </div>
             <div className="h-8 w-px bg-slate-200"></div>
             <div>
               <div className="text-[10px] font-bold text-slate-400 uppercase">Health Score</div>
               <div className={`text-sm font-bold ${graphData.graph_health > 80 ? 'text-emerald-500' : 'text-amber-500'}`}>{graphData.graph_health}/100</div>
             </div>
          </div>
        )}
      </div>

      {/* Inspector Panel */}
      {selectedNode && (
        <div className="w-[320px] bg-white border-l border-slate-200 shadow-xl z-20 flex flex-col">
          <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
            <h2 className="text-sm font-bold text-slate-800 flex items-center"><Settings2 size={16} className="mr-2 text-indigo-500"/> Node Inspector</h2>
            <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-slate-600 font-bold">×</button>
          </div>
          
          <div className="p-6 space-y-6 flex-1 overflow-y-auto">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">Beat Type</span>
              <span className="text-sm font-medium text-slate-700 capitalize">{selectedNode.data.beat_type}</span>
            </div>
            
            <div>
               <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">Confidence</span>
               <div className="flex items-center">
                 <div className="w-full bg-slate-200 rounded-full h-2.5 mr-2">
                    <div className={`h-2.5 rounded-full ${selectedNode.data.confidence < 80 ? 'bg-amber-400' : 'bg-emerald-400'}`} style={{ width: `${selectedNode.data.confidence}%` }}></div>
                 </div>
                 <span className="text-xs font-bold text-slate-600">{selectedNode.data.confidence}%</span>
               </div>
               {selectedNode.data.confidence < 80 && (
                 <div className="mt-2 text-[10px] text-amber-700 bg-amber-50 p-2 rounded flex items-start border border-amber-200">
                   <AlertTriangle size={12} className="mr-1 mt-0.5 shrink-0" /> Consider overriding this node's intent manually to ensure reliable execution.
                 </div>
               )}
            </div>

            <div className="border-t border-slate-200 my-4"></div>

            <div>
              <h3 className="text-sm font-bold text-slate-800 mb-3">Semantic Overrides</h3>
              <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                Overriding the intent patches the execution graph directly. The raw text script will remain unmodified.
              </p>
              
              <label className="text-xs font-bold text-slate-700 mb-2 block">Active Intent</label>
              <input 
                type="text" 
                value={newIntent}
                onChange={e => setNewIntent(e.target.value)}
                className="w-full outline-none text-sm border border-slate-300 rounded p-2 focus:border-indigo-500 mb-3"
              />
              
              <button 
                onClick={handleOverride}
                disabled={newIntent === selectedNode.data.intent}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white py-2 rounded shadow font-medium text-sm transition-colors"
              >
                Apply Override Patch
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
