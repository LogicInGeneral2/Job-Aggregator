'use client';

import { useState } from 'react';
// 1. Added trackJobClick to the imports
import { searchJobs, ApiResponse, trackJobClick } from '../../services/api';

export default function Omnibox() {
    const [query, setQuery] = useState('');
    const [result, setResult] = useState<ApiResponse | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            const data = await searchJobs(query);
            console.log('Search results:', data); // Debugging line
            setResult(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-4xl flex flex-col items-center mt-12">
            <form onSubmit={handleSearch} className="w-full flex gap-2">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for 'Kubernetes' or 'Golang'..."
                    className="w-full p-4 border-2 border-gray-300 rounded-lg text-lg focus:outline-none focus:border-blue-500"
                />
                <button 
                    type="submit" 
                    className="px-8 py-4 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition"
                >
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </form>

            {/* Search Results Display */}
            {result && result.data.length > 0 && (
                <div className="w-full mt-8">
                    <h3 className="text-xl font-bold mb-4">Search Results</h3>
                    <div className="grid gap-4">
                        {result.data.map((job) => (
                            <div key={job.id} className="p-4 border rounded-lg bg-gray-50 hover:shadow-md transition">
                                <h4 className="font-semibold text-lg">{job.title}</h4>
                                {/* Added category to the display */}
                                <p className="text-gray-600">{job.company} • {job.category}</p>
                                
                                {/* 2. Added the clickable link with the onClick tracker! */}
                                <a 
                                    href={job.url} 
                                    target="_blank" 
                                    rel="noreferrer" 
                                    onClick={() => trackJobClick(job.id, job.category)} 
                                    className="text-blue-500 text-sm mt-2 inline-block font-medium"
                                >
                                    View Application &rarr;
                                </a>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {result && result.data.length === 0 && (
                <p className="mt-8 text-gray-500">No jobs found matching "{query}".</p>
            )}
        </div>
    );
}