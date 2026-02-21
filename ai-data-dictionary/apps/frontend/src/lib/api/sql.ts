/**
 * SQL Execution API functions
 */

import { apiClient } from "../api-client";

export interface SQLValidationRequest {
  sql: string;
  context?: string;
}

export interface SQLValidationResponse {
  valid: boolean;
  is_read_only: boolean;
  error?: string;
  formatted_sql?: string;
  tables?: string[];
  llm_analysis?: {
    issues?: string[];
    suggestions?: string[];
    security_concerns?: string[];
  };
}

export interface SQLExecutionRequest {
  sql: string;
  validate_with_llm?: boolean;
  allow_write?: boolean;
}

export interface SQLExecutionResponse {
  success: boolean;
  rows_affected?: number;
  data?: Record<string, any>[];
  columns?: string[];
  execution_time_ms?: number;
  error?: string;
  validation?: any;
}

export interface NaturalLanguageToSQLRequest {
  question: string;
  schema_context: string;
}

export interface NaturalLanguageToSQLResponse {
  sql?: string;
  explanation?: string;
  confidence?: number;
  validation?: any;
  error?: string;
}

export interface SQLExplanationRequest {
  sql: string;
}

export interface SQLExplanationResponse {
  summary?: string;
  detailed_steps?: string[];
  error?: string;
}

/**
 * Validate SQL query
 */
export async function validateSQL(
  request: SQLValidationRequest,
  token: string
): Promise<SQLValidationResponse> {
  return apiClient.post<SQLValidationResponse>("/sql/validate", request, token);
}

/**
 * Execute SQL query
 */
export async function executeSQL(
  request: SQLExecutionRequest,
  token: string
): Promise<SQLExecutionResponse> {
  return apiClient.post<SQLExecutionResponse>("/sql/execute", request, token);
}

/**
 * Generate SQL from natural language
 */
export async function generateSQL(
  request: NaturalLanguageToSQLRequest,
  token: string
): Promise<NaturalLanguageToSQLResponse> {
  return apiClient.post<NaturalLanguageToSQLResponse>(
    "/sql/generate",
    request,
    token
  );
}

/**
 * Explain SQL query
 */
export async function explainSQL(
  request: SQLExplanationRequest,
  token: string
): Promise<SQLExplanationResponse> {
  return apiClient.post<SQLExplanationResponse>("/sql/explain", request, token);
}

/**
 * Format SQL query
 */
export async function formatSQL(
  sql: string,
  token: string
): Promise<{ formatted_sql: string }> {
  return apiClient.post<{ formatted_sql: string }>(
    `/sql/format?sql=${encodeURIComponent(sql)}`,
    {},
    token
  );
}
