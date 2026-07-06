'use client';

import { useEffect, useState } from 'react';
import { fetchUserProfile, removeUserPreference, resetUserProfile } from '../services/api';

interface Preference {
    category: string;
    score: number;
}

export default function UserProfile() {
    const [preferences, setPreferences] = useState<Preference[]>([]);
    const [sessionId, setSessionId] = useState<string | null>(null);

    // 1. Load the profile
    const loadProfile = async () => {
        const sid = localStorage.getItem('session_id');
        if (!sid) return;
        setSessionId(sid);
        
        try {
            const data = await fetchUserProfile(sid);
            setPreferences(data.preferences);
        } catch (error) {
            console.error("Error loading profile", error);
        }
    };

    useEffect(() => {
        loadProfile();
        // Poll to update
        const interval = setInterval(loadProfile, 5000);
        return () => clearInterval(interval);
    }, []);

    // 2. Single Deletion
    const handleRemove = async (category: string) => {
        if (!sessionId) return;
        await removeUserPreference(sessionId, category);
        loadProfile();
    };

    // 3. Full Reset
    const handleReset = async () => {
        if (!sessionId) return;
        await resetUserProfile(sessionId);
        setPreferences([]); 
    };

    if (!sessionId || preferences.length === 0) {
        return (
            <div className="p-4 rounded-xl border border-gray-300 shadow-sm">
                <h3 className="text-lg font-bold mb-2">My Preferred Jobs</h3>
                <p className="text-sm text-gray-500">No behavioral data tracked yet. Click some jobs!</p>
            </div>
        );
    }

    return (
        <div className="p-4 rounded-xl border border-gray-300 shadow-sm">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold mb-2">My Preferred Jobs</h3>
                <button 
                    onClick={handleReset}
                    className="text-xs px-4 py-2 bg-green-700 font-bold rounded-md hover:bg-green-500 transition"
                >
                    Reset Profile
                </button>
            </div>
            
            <p className="text-xs text-gray-500 mb-4">
                We use your clicks to boost relevant search results. You control your data.
            </p>

            <ul className="space-y-4">
                {preferences.map((pref) => (
                    <li key={pref.category} className="flex justify-between items-center p-4 rounded-lg border border-gray-500 hover:border-green-500 transition">
                        <div>
                            <span className="font-semibold block">{pref.category}</span>
                            <span className="text-xs text-gray-500">Affinity Score: {pref.score}</span>
                        </div>
                        <button 
                            onClick={() => handleRemove(pref.category)}
                            className="text-sm text-green-700 hover:text-green-500 transition px-2 py-1 rounded-md"
                        >
                            X
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}