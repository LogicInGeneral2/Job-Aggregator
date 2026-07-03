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
            <div className="p-6 bg-gray-50 rounded-xl border border-gray-200">
                <h3 className="text-lg font-bold text-gray-700 mb-2">My Analytics Profile</h3>
                <p className="text-sm text-gray-500">No behavioral data tracked yet. Click some jobs!</p>
            </div>
        );
    }

    return (
        <div className="p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-800">My Analytics Profile</h3>
                <button 
                    onClick={handleReset}
                    className="text-xs px-3 py-1 bg-red-100 text-red-600 rounded-md hover:bg-red-200 transition"
                >
                    Reset Profile
                </button>
            </div>
            
            <p className="text-xs text-gray-500 mb-4">
                We use your clicks to boost relevant search results. You control your data.
            </p>

            <ul className="space-y-2">
                {preferences.map((pref) => (
                    <li key={pref.category} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <div>
                            <span className="font-semibold text-gray-700 block">{pref.category}</span>
                            <span className="text-xs text-gray-400">Affinity Score: {pref.score}</span>
                        </div>
                        <button 
                            onClick={() => handleRemove(pref.category)}
                            className="text-sm text-gray-400 hover:text-red-500 transition"
                            title="Remove from profile"
                        >
                            X
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}