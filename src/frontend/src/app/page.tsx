'use client';

import Heatmap from '@/components/Globe';
import JobList from '@/components/JobList';
import Omnibox from '@/components/Omnibox';
import TrendingJobs from '@/components/TrendingJobs';
import TrendingSkills from '@/components/TrendingSkills';
import UserProfile from '@/components/UserProfile';
import { ApiResponse, searchJobs } from '@/services/api';
import { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<ApiResponse | null>(null);

    const handleSearch = async (query: string) => {
        const data = await searchJobs(query);

        setQuery(query);
        setResult(data);
    };
  
  return (
    <main className="min-h-screen flex flex-col items-center p-12 font-sans">
      
      <div className="text-center mb-4">
        <h1 className="text-4xl font-extrabold tracking-tight">Job Board Aggregator</h1>
        <p className="text-gray-300 mt-2">Sourced from Remotive, Jobicy, and Greenhouse</p>
      </div>

      <Heatmap />

      <Omnibox onSearch={handleSearch} />

            
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Column: Job Feed (Takes up 2/3 of the screen) */}
        <div className="md:col-span-2">

            {result ? (
                <>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">
                        Search Results for "{query}"
                    </h3>
                    <button
                        onClick={() => {
                            setResult(null);
                            setQuery('');
                        }}
                        className="text-sm text-green-500 hover:underline"
                    >
                        ← Back to Trending Jobs
                    </button>
                  </div>

                  {result.data.length > 0 ? (
                      <JobList jobs={result.data} />
                  ) : (
                      <p>No jobs found.</p>
                  )}
                </>
            ) : (
                <TrendingJobs />
            )}

        </div>
        
        {/* Right Column: Sidebar (Takes up 1/3 of the screen) */}
        <div className="md:col-span-1 space-y-6">
            <TrendingSkills />
            <UserProfile />
        </div>
      </section>

    </main>
  );
}