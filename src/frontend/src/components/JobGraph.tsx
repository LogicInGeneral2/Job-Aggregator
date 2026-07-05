'use client';

import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import { expandGraphNode } from '../services/api';
import { useGraphContext } from '@/context/GraphContext';

const CytoscapeComponent = dynamic(() => import('react-cytoscapejs'), { ssr: false });
const API_BASE_URL = 'http://localhost:8000/api';

export default function JobGraphDashboard() {
    const { elements, setElements, sessionId } = useGraphContext();
    
    // Canvas & UI State
    const [selectedNode, setSelectedNode] = useState<any | null>(null);
    const [toolbarPos, setToolbarPos] = useState({ x: 0, y: 0 });
    const cyRef = useRef<any>(null);

    useEffect(() => {
        if (cyRef.current && elements.length > 0) {
            setTimeout(() => cyRef.current.layout({ 
                name: 'cose', 
                animate: true,
                randomize: true,    
                nodeRepulsion: 400000
            }).run(), 200);
        }
    }, [elements]);



    const trackJobClick = async (jobId: string, category: string) => {
        try {
            await fetch(`${API_BASE_URL}/jobs/click`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, job_id: String(jobId), category: category || 'unknown' })
            });
        } catch (err) { console.error('Click tracking error:', err); }
    };

    const setupCy = (cy: any) => {
        cyRef.current = cy;
        cy.on('tap', 'node', (evt: any) => {
            const node = evt.target;
            const position = node.renderedPosition();
            setSelectedNode(node.data());
            setToolbarPos({ x: position.x, y: position.y });
        });
        
        cy.on('tap', (evt: any) => { if (evt.target === cy) setSelectedNode(null); });
        cy.on('pan zoom', () => setSelectedNode(null));
    };

    const handleExpand = async () => {
        if (!selectedNode || !sessionId) return;
        try {
            const data = await expandGraphNode(selectedNode.id, sessionId);
            if (data.nodes.length > 0) {
                setElements(prev => [...prev, ...data.nodes, ...data.edges]);
            }
            setSelectedNode(null);
        } catch (e) { console.error(e); }
    };

    const handleRemove = () => {
        if (!selectedNode || !cyRef.current) return;
        cyRef.current.getElementById(selectedNode.id).remove();
        setSelectedNode(null);
    };

    const handleApply = async () => {
        if (!selectedNode || selectedNode.type !== 'job') return;
        await trackJobClick(selectedNode.id, selectedNode.details.category);
        window.open(selectedNode.details?.url, '_blank');
        setSelectedNode(null);
    };

    return (
        <div className="flex flex-col h-[800px] border border-gray-200 rounded-xl overflow-hidden bg-white shadow-lg mt-6">
            <div className="flex flex-1 relative overflow-hidden">
                {/* CYTOSCAPE CANVAS AREA */}
                <div className="flex-1 relative bg-[#f8fafc]">
                    {elements.length === 0 ? (
                        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                            Use the Omnibox to add your first node to the graph.
                        </div>
                    ) : (
                        <CytoscapeComponent 
                            elements={elements} 
                            style={{ width: '100%', height: '100%' }} 
                            cy={setupCy}
                            stylesheet={[
                                {
                                    selector: 'node',
                                    style: {
                                        'label': 'data(label)',
                                        'text-valign': 'bottom',
                                        'text-margin-y': 5,
                                        'font-size': '12px',
                                        'background-color': '#3b82f6',
                                        'color': '#334155'
                                    }
                                },
                                {
                                    selector: 'node[type="job"]',
                                    style: { 'background-color': '#10b981', 'shape': 'hexagon', 'width': 40, 'height': 40 }
                                },
                                {
                                    selector: 'edge',
                                    style: { 'width': 2, 'line-color': '#cbd5e1', 'curve-style': 'bezier' }
                                }
                            ]}
                        />
                    )}

                    {/* FLOATING TOOLBAR */}
                    {selectedNode && (
                        <div className="absolute z-10 bg-white border border-gray-200 shadow-xl rounded-lg flex space-x-1 p-1"
                             style={{ top: toolbarPos.y - 50, left: toolbarPos.x + 20 }}>
                            <button onClick={handleExpand} className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded">➕ Expand</button>
                            {selectedNode.type === 'job' && (
                                <button onClick={handleApply} className="px-3 py-1 text-sm text-green-600 hover:bg-green-50 rounded">📌 Apply</button>
                            )}
                            <button onClick={handleRemove} className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded">✖ Remove</button>
                        </div>
                    )}
                </div>

                {/* SIDE PANEL */}
                <div className="w-96 bg-white border-l border-gray-200 flex flex-col shadow-inner">
                    <div className="p-6 overflow-y-auto flex-1">
                        <div>
                            {selectedNode ? (
                                <>
                                    <span className="text-xs font-bold text-gray-400 uppercase">{selectedNode.type}</span>
                                    <h3 className="text-xl font-bold text-gray-800 mt-1 mb-4">{selectedNode.label}</h3>
                                    
                                    {selectedNode.type === 'job' && selectedNode.details ? (
                                        <div className="space-y-4">
                                            <p className="text-sm text-gray-600"><strong>Company:</strong> {selectedNode.details.company}</p>
                                            <p className="text-sm text-gray-600"><strong>Location:</strong> {selectedNode.details.location}</p>
                                            <p className="text-sm text-gray-600"><strong>Category:</strong> {selectedNode.details.category}</p>
                                            <p className="text-sm text-gray-600"><strong>Description:</strong> {selectedNode.details.description}</p>
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500 italic">Expand this node on the canvas to find specific job postings.</p>
                                    )}
                                </>
                            ) : (
                                <div className="text-center text-gray-400 mt-10">
                                    Click any node on the canvas to view its details here.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}