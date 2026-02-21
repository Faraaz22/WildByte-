/**
 * Tables API: list tables (paginated, filter by schema), get table detail.
 */

import { apiClient } from "../api-client";
import { AuthStore } from "../auth-store";

export interface TableResponse {
  id: number;
  schema_id: number;
  name: string;
  table_type: string;
  description: string | null;
  ai_generated_description: string | null;
  row_count: number | null;
  size_bytes: number | null;
  has_quality_issues: boolean;
  completeness_pct: number | null;
  freshness_hours: number | null;
  created_at: string;
  updated_at: string;
  last_analyzed_at: string | null;
}

export interface TableListResponse {
  data: TableResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ColumnResponse {
  id: number;
  table_id: number;
  name: string;
  data_type: string;
  ordinal_position: number;
  is_nullable: boolean;
  is_primary_key?: boolean;
  is_foreign_key?: boolean;
}

export interface TableDetailResponse extends TableResponse {
  columns: ColumnResponse[];
  use_cases?: string[] | null;
  freshness_assessment?: string | null;
  considerations?: string[] | null;
  metadata_json?: Record<string, unknown> | null;
}

function getToken(): string | null {
  return AuthStore.getToken();
}

export async function listTables(params?: {
  page?: number;
  page_size?: number;
  schema_id?: number;
  search?: string;
}): Promise<TableListResponse> {
  const sp = new URLSearchParams();
  if (params?.page != null) sp.set("page", String(params.page));
  if (params?.page_size != null) sp.set("page_size", String(params.page_size));
  if (params?.schema_id != null) sp.set("schema_id", String(params.schema_id));
  if (params?.search) sp.set("search", params.search);
  const qs = sp.toString() ? `?${sp.toString()}` : "";
  return apiClient.get<TableListResponse>(`/tables${qs}`, getToken() ?? undefined);
}

export async function getTable(tableId: number): Promise<TableDetailResponse> {
  return apiClient.get<TableDetailResponse>(`/tables/${tableId}`, getToken() ?? undefined);
}
