// Auth utilities for token management
const TOKEN_KEY = 'lawscout_auth_token';
const USER_KEY = 'lawscout_user';

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

// Token management
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// User data management
export function getUser(): User | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

export function setUser(user: User): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export function logout(): void {
  removeToken();
  // Optionally redirect to login page
  if (typeof window !== 'undefined') {
    window.location.href = '/';
  }
}

