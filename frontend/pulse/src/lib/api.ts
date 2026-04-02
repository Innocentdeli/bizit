export const API_BASE_URL = 'http://localhost:8002';

export async function fetchAPI(endpoint: string) {
    try {
        const res = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!res.ok) {
            throw new Error(`API Error: ${res.statusText}`);
        }
        return await res.json();
    } catch (error) {
        console.error(`Failed to fetch ${endpoint}:`, error);
        return null;
    }
}
