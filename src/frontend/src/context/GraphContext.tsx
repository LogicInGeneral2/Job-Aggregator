'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { initGraph, fetchUserProfile } from '../services/api'; 

interface GraphContextType {
    elements: any[];
    setElements: React.Dispatch<React.SetStateAction<any[]>>;
    sessionId: string;
    addQueryToGraph: (query: string) => Promise<void>;
    currentQuery: string;
    setCurrentQuery: (query: string) => void;
}

const GraphContext = createContext<GraphContextType | undefined>(undefined);

export function GraphProvider({ children }: { children: React.ReactNode }) {
    const [elements, setElements] = useState<any[]>([]);
    const [sessionId, setSessionId] = useState<string>('');
    const [currentQuery, setCurrentQuery] = useState<string>('');

    // Initialize session and restore past data
    useEffect(() => {
        let sid = localStorage.getItem('session_id');
        if (!sid) {
            sid = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('session_id', sid);
        }
        setSessionId(sid);
        
        // Restore the last searched query if they refresh
        const savedQuery = localStorage.getItem('last_search_query');
        if (savedQuery) setCurrentQuery(savedQuery);

        // Restore graph nodes from backend
        fetchUserProfile(sid)
            .then(data => {
                if (data && data.nodes && data.nodes.length > 0) {
                    setElements([...data.nodes, ...data.edges]);
                }
            })
            .catch(console.error);
    }, []);

    const addQueryToGraph = async (query: string) => {
        if (!sessionId) return;
        
        // Save to Context and LocalStorage simultaneously
        setCurrentQuery(query);
        localStorage.setItem('last_search_query', query);

        try {
            const data = await initGraph(query, sessionId);
            setElements(prev => {
                const existingIds = new Set(prev.map(el => el.data.id));
                const newElements = [...data.nodes, ...data.edges].filter(el => !existingIds.has(el.data.id));
                return [...prev, ...newElements];
            });
        } catch (error) {
            console.error("Error adding to graph", error);
        }
    };

    return (
        <GraphContext.Provider value={{ elements, setElements, sessionId, addQueryToGraph, currentQuery, setCurrentQuery }}>
            {children}
        </GraphContext.Provider>
    );
}

export function useGraphContext() {
    const context = useContext(GraphContext);
    if (!context) throw new Error("useGraphContext must be used within a GraphProvider");
    return context;
}