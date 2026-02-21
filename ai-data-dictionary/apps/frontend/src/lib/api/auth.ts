/**
 * Authentication API functions
 */

import { apiClient } from "../api-client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    username: string;
    full_name?: string;
    role: string;
    is_active: boolean;
  };
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: string;
  is_active: boolean;
}

/**
 * Login user
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  return apiClient.post<LoginResponse>("/auth/login", credentials);
}

/**
 * Logout user
 */
export async function logout(token: string): Promise<{ message: string }> {
  return apiClient.post<{ message: string }>("/auth/logout", {}, token);
}

/**
 * Refresh access token
 */
export async function refreshToken(
  refreshTokenData: RefreshTokenRequest
): Promise<RefreshTokenResponse> {
  return apiClient.post<RefreshTokenResponse>("/auth/refresh", refreshTokenData);
}

/**
 * Get current user information
 */
export async function getCurrentUser(token: string): Promise<UserResponse> {
  return apiClient.get<UserResponse>("/auth/me", token);
}
