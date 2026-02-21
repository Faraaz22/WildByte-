/**
 * Auth API: login (username + password), logout, refresh, me.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";
const API_V1 = "/api/v1";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_hours: number;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: string;
  full_name: string | null;
  is_active: boolean;
}

async function request<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...init } = options;
  const url = `${API_BASE}${API_V1}${path}`;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...init, headers });
  const contentType = res.headers.get("content-type");
  const isJson = contentType?.includes("application/json");
  const body = isJson ? await res.json() : null;

  if (!res.ok) {
    const d = body?.detail;
    const msg =
      typeof d === "string" ? d : Array.isArray(d) ? d.map((x: { msg?: string }) => x.msg || "").join(", ") : `HTTP ${res.status}`;
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return body as T;
}

export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export async function logout(): Promise<{ message: string }> {
  const token = getToken();
  return request<{ message: string }>("/auth/logout", {
    method: "POST",
    token: token ?? undefined,
  });
}

export async function refreshAccessToken(): Promise<TokenResponse> {
  const token = getToken();
  if (!token) throw new Error("No token");
  return request<TokenResponse>("/auth/refresh", {
    method: "POST",
    token,
  });
}

export async function getCurrentUser(token: string): Promise<UserResponse> {
  return request<UserResponse>("/auth/me", { method: "GET", token });
}
