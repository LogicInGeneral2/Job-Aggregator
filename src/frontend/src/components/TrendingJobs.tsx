'use client';

import { useEffect, useState } from 'react';
import { fetchRecentJobs, ApiResponse, trackJobClick } from '../services/api';
import JobList from './JobList';

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

    if (loading) return <div className="text-gray-500">Loading recent jobs...</div>;
    if (!result) return null;

    return (
        <div className="w-full">
            <h3 className="text-xl font-bold">Recent Jobs</h3>
            <JobList jobs={result.data} />
        </div>
    );
}