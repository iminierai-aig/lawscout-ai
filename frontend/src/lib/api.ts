// API client for LawScout AI backend
// Next.js replaces NEXT_PUBLIC_* vars at build time
declare const process: {
  env: {
    NEXT_PUBLIC_API_URL?: string;
  };
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.lawscoutai.com';

// Types matching backend schemas
export interface User {
  id: number;
  email: string;
  full_name: string | null;
  tier: string;
  search_count: number;
  searches_remaining: number;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SearchLimitResponse {
  can_search: boolean;
  tier: string;
  searches_remaining: number;
  message: string;
}

export interface ApiError {
  detail: string;
}

// Helper to handle API errors
async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const error: ApiError = await res.json().catch(() => ({ detail: 'Unknown error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${res.status}`);
  }
  return res.json();
}

// Auth API functions
export async function register(email: string, password: string, fullName: string): Promise<TokenResponse> {
  const res = await fetch(`${API_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName })
  });
  return handleResponse<TokenResponse>(res);
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', email);  // OAuth2PasswordRequestForm uses 'username' field
  formData.append('password', password);
  
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  });
  return handleResponse<TokenResponse>(res);
}

export async function getUser(token: string): Promise<User> {
  const res = await fetch(`${API_URL}/api/auth/me`, {
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return handleResponse<User>(res);
}

export async function checkSearchLimit(token: string): Promise<SearchLimitResponse> {
  const res = await fetch(`${API_URL}/api/auth/search/check-limit`, {
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return handleResponse<SearchLimitResponse>(res);
}

export async function trackSearch(
  token: string, 
  query: string, 
  collection?: string, 
  resultCount?: number
): Promise<{ message: string; search_count: number; searches_remaining: number }> {
  const res = await fetch(`${API_URL}/api/auth/search/track`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query, collection, result_count: resultCount })
  });
  return handleResponse(res);
}

