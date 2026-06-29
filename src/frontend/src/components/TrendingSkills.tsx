"use client";

import { useEffect, useState } from 'react';
import { fetchTrendingSkills } from '../services/api';

interface Skill {
  skill: string;
  count: number;
}

export default function TrendingSkills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSkills = async () => {
      try {
        const data = await fetchTrendingSkills();
        setSkills(data.trending || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    loadSkills();
  }, []);

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-4 bg-gray-200 rounded w-full"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 text-sm p-4 bg-red-50 rounded-lg">Error: {error}</div>;
  }

  return (
    <div className="p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        📈 Live Trending Skills
      </h2>
      
      <ul className="space-y-3">
        {skills.map((s, index) => (
          <li key={s.skill} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded-md transition-colors">
            <div className="flex items-center gap-3">
              <span className="text-gray-400 font-mono text-sm w-4">{index + 1}.</span>
              <span className="font-semibold text-gray-700">{s.skill}</span>
            </div>
            <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2.5 py-1 rounded-full">
              {s.count} mentions
            </span>
          </li>
        ))}
      </ul>
      
      <div className="mt-5 pt-4 border-t border-gray-100 flex justify-end">
        <span className="text-xs font-medium text-gray-400 bg-gray-50 px-2 py-1 rounded">
          ⚡ Served instantly via Redis ZSET
        </span>
      </div>
    </div>
  );
}