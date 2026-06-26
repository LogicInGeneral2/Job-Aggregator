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

export const searchJobs = async (query: string): Promise<ApiResponse> => {
    //Elasticsearch endpoint
    const response = await fetch(`${API_BASE_URL}/jobs/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Failed to search jobs');
    return response.json();
};