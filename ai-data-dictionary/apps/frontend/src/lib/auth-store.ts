/**
 * Minimal auth store (localStorage). Token + optional user.
 */

const TOKEN_KEY = "access_token";
const USER_KEY = "user";

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string | null;
  role: string;
  is_active: boolean;
}

export const AuthStore = {
  getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(TOKEN_KEY, token);
  },

  getUser(): User | null {
    if (typeof window === "undefined") return null;
    const s = localStorage.getItem(USER_KEY);
    return s ? (JSON.parse(s) as User) : null;
  },

  setUser(user: User): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  setAuth(data: { access_token: string; user?: User }): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(TOKEN_KEY, data.access_token);
    if (data.user) localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  },

  clearAuth(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};
