/**
 * Databases API: list, create from URI, test connection, sync.
 */

import { apiClient } from "../api-client";
import { AuthStore } from "../auth-store";

export interface DatabaseResponse {
  id: number;
  name: string;
  db_type: string;
  description: string | null;
  host: string | null;
  port: number | null;
  database_name: string | null;
  last_sync_at: string | null;
  sync_status: string;
  sync_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface DatabaseListResponse {
  data: DatabaseResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TestConnectionResponse {
  connected: boolean;
  message?: string;
}

export interface SyncResponse {
  status: string;
  message?: string;
  database_id: number;
  schemas?: number;
  tables?: number;
  columns?: number;
  lineage_edges?: number;
}

function getToken(): string | null {
  return AuthStore.getToken();
}

export async function listDatabases(): Promise<DatabaseListResponse> {
  return apiClient.get<DatabaseListResponse>("/databases", getToken() ?? undefined);
}

export async function testConnection(connectionUri: string): Promise<TestConnectionResponse> {
  return apiClient.post<TestConnectionResponse>(
    "/databases/test-connection",
    { connection_uri: connectionUri },
    getToken() ?? undefined
  );
}

export async function createDatabaseFromUri(
  name: string,
  connectionUri: string,
  description?: string
): Promise<DatabaseResponse> {
  return apiClient.post<DatabaseResponse>(
    "/databases/from-uri",
    { name, connection_uri: connectionUri, description: description ?? null },
    getToken() ?? undefined
  );
}

export async function syncDatabase(databaseId: number): Promise<SyncResponse> {
  return apiClient.post<SyncResponse>(
    `/databases/${databaseId}/sync`,
    undefined,
    getToken() ?? undefined
  );
}
