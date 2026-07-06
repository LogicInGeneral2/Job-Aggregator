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
      <div className="p-4 rounded-lg shadow-sm border border-gray-500 animate-pulse">
        <div className="h-4 rounded w-1/2 mb-4"></div>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-4 bg-gray-300 rounded w-full"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 text-sm p-4 bg-red-50 rounded-lg">Error: {error}</div>;
  }

  return (
    <div className="p-4 rounded-lg shadow-sm border border-gray-500">
      <h2 className="text-xl font-bold mb-4 flex items-center">
        Trending Skills
      </h2>
      
      <ul className="space-y-4">
        {skills.map((s, index) => (
          <li key={s.skill} className="flex justify-between items-center px-4 rounded-lg">
            <div className="flex items-center font-semibold text-sm">
              <span>{index + 1}. {s.skill}</span>
            </div>
            <span className="bg-green-700 text-white-800 text-xs font-bold p-2 rounded-full">
              {s.count} mentions
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}