'use client';

import { useEffect, useState } from 'react';
import { fetchRecentJobs, ApiResponse, trackJobClick } from '../services/api';

export default function TrendingJobs() {
    const [result, setResult] = useState<ApiResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadJobs = async () => {
            try {
                const data = await fetchRecentJobs();
                setResult(data);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        loadJobs();
    }, []);

    if (loading) return <div className="text-gray-500">Loading trending jobs...</div>;
    if (!result) return null;

    return (
        <div className="w-full max-w-4xl mt-8">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Trending Jobs</h2>
                {/* The Flex: Proving Redis works [cite: 1011] */}
                <span className={`text-xs px-2 py-1 rounded-full ${result.source === 'redis' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                    ⚡ Served from {result.source}
                </span>
            </div>

            <div className="grid gap-4">
                {result.data.map((job) => (
                    <div key={job.id} className="p-4 border rounded-lg shadow-sm hover:shadow-md transition">
                        <h3 className="font-semibold text-lg">{job.title}</h3>
                        <p className="text-gray-600">{job.company} • {job.category}</p>
                        <a href={job.url} target="_blank" rel="noreferrer" onClick={() => trackJobClick(job.id, job.category)} className="text-blue-500 text-sm mt-2 inline-block">
                            View Application &rarr;
                        </a>
                    </div>
                ))}
            </div>
        </div>
    );
}