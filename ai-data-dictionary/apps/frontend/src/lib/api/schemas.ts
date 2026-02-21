/**
 * Schemas API: list schemas (optionally by database_id).
 */

import { apiClient } from "../api-client";
import { AuthStore } from "../auth-store";

export interface SchemaResponse {
  id: number;
  database_id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  table_count?: number;
}

function getToken(): string | null {
  return AuthStore.getToken();
}

export async function listSchemas(databaseId?: number): Promise<SchemaResponse[]> {
  const qs = databaseId != null ? `?database_id=${databaseId}` : "";
  return apiClient.get<SchemaResponse[]>(`/schemas${qs}`, getToken() ?? undefined);
}

export async function listDatabaseSchemas(databaseId: number): Promise<SchemaResponse[]> {
  return apiClient.get<SchemaResponse[]>(
    `/databases/${databaseId}/schemas`,
    getToken() ?? undefined
  );
}
