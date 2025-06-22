// API Configuration for InstantDashboard
// Automatically detects environment and uses correct API URL

function getApiUrl(): string {
  // If we're in the browser
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // If accessing through ngrok (contains ngrok in hostname)
    if (hostname.includes('ngrok')) {
      // Call the backend locally since it's on the same machine
      return 'http://localhost:8001';
    }
    
    // If accessing through localhost
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8001';
    }
    
    // Default fallback
    return 'http://localhost:8001';
  }
  
  // Server-side rendering fallback
  return 'http://localhost:8001';
}

export const API_URL = getApiUrl();

// Helper function for making API calls
export function apiCall(endpoint: string, options?: RequestInit) {
  const url = `${API_URL}${endpoint}`;
  console.log('API Call:', url);
  
  return fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
} 