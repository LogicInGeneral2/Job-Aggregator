'use client';

import { useState } from 'react';


type OmniboxProps = {
    onSearch: (query: string) => Promise<void>;
};

export default function Omnibox({ onSearch }: OmniboxProps) {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        await onSearch(query);
        setLoading(false);
    };

    return (
        <>
            <form onSubmit={handleSearch} className="w-full max-w-4xl flex">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for 'Kubernetes' or 'Golang'..."
                    className="w-full p-2 border border-r-0 border-gray-300 rounded-lg rounded-r-none text-lg focus:outline-none focus:border-green-700"
                />
                <button 
                    type="submit" 
                    className="py-2 bg-green-700 rounded-lg rounded-l-none font-bold hover:bg-green-500 transition w-40"
                >
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </form>

            <div className="w-full max-w-4xl border-t my-8 border-gray-300"></div>
        </>
    );
}