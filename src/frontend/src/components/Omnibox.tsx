'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useGraphContext } from '@/context/GraphContext';

export default function Omnibox() {
    const [localInput, setLocalInput] = useState('');
    const router = useRouter();
    const pathname = usePathname(); 
    
    // Pull exactly what we need from Context
    const { addQueryToGraph } = useGraphContext();

    const isOnGraphPage = pathname === '/graph';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!localInput.trim()) return;

        // Add the query to the context (which handles the API call and localStorage)
        await addQueryToGraph(localInput);
        setLocalInput(''); // Clear the input field

        // If they are on the homepage, route them to the graph dashboard WITHOUT query params
        if (!isOnGraphPage) {
            router.push(`/graph`);
        }
    };

    return (
        <div className="w-full max-w-4xl flex flex-col items-center mt-12">
            <form onSubmit={handleSubmit} className="w-full flex gap-2">
                <input
                    type="text"
                    value={localInput}
                    onChange={(e) => setLocalInput(e.target.value)}
                    placeholder="Search for 'Kubernetes' or 'Golang'..."
                    className="w-full p-4 border-2 border-gray-300 rounded-lg text-lg focus:outline-none focus:border-blue-500"
                />
                <button 
                    type="submit" 
                    className="px-8 py-4 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition"
                >
                    {isOnGraphPage ? 'Add' : 'Search'}
                </button>
            </form>
        </div>
    );
}