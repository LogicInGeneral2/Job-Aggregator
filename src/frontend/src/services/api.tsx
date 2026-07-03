const API_BASE_URL = 'http://localhost:8000/api';

export interface Job {
    id: string;
    title: string;
    company: string;
    url: string;
    category: string;
    publication_date: string;
}

export interface ApiResponse {
    source: 'redis' | 'elasticsearch';
    data: Job[];
}

export const fetchRecentJobs = async (): Promise<ApiResponse> => {
    //Redis cache endpoint
    const response = await fetch(`${API_BASE_URL}/jobs/recent`);
    if (!response.ok) throw new Error('Failed to fetch recent jobs');
    return response.json();
};

export const searchJobs = async (query: string) => {
    // 1. Grab tracking ID
    const sessionId = localStorage.getItem('session_id');
    
    // 2. Append it 
    let url = `${API_BASE_URL}/jobs/search?q=${encodeURIComponent(query)}`;
    if (sessionId) {
        url += `&session_id=${encodeURIComponent(sessionId)}`;
    }

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Failed to search jobs');
    }

    
    return response.json();
};

export const fetchTrendingSkills = async () => {
    const response = await fetch(`${API_BASE_URL}/skills/trending`);
    if (!response.ok) {
        throw new Error('Failed to fetch trending skills');
    }
    return response.json();
};

export const trackJobClick = async (jobId: string, category: string) => {
    try {
        // Retrieve or generate a unique Session ID for browser
        let sessionId = localStorage.getItem('session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('session_id', sessionId);
        }

        const response = await fetch(`${API_BASE_URL}/jobs/click`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                job_id: String(jobId),
                category: category || 'unknown'
            })
        });

        if (!response.ok) {
            console.error('Failed to log click event');
        }
    } catch (err) {
        console.error('Click tracking error:', err);
    }
};

export const fetchHeatmapData = async () => {
    const response = await fetch(`${API_BASE_URL}/jobs/heatmap`);
    if (!response.ok) throw new Error('Failed to fetch heatmap data');
    return response.json();
};

export const fetchUserProfile = async (sessionId: string) => {
    const response = await fetch(`${API_BASE_URL}/profile/${sessionId}`);
    if (!response.ok) throw new Error('Failed to fetch profile');
    return response.json();
};

export const removeUserPreference = async (sessionId: string, category: string) => {
    // encodeURIComponent ensures spaces in categories (like "Software Development") don't break the URL
    const response = await fetch(`${API_BASE_URL}/profile/${sessionId}/preferences/${encodeURIComponent(category)}`, {
        method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove preference');
    return response.json();
};

export const resetUserProfile = async (sessionId: string) => {
    const response = await fetch(`${API_BASE_URL}/profile/${sessionId}`, {
        method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to reset profile');
    return response.json();
};