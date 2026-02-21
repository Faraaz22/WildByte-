/**
 * Lineage API: full graph (nodes + edges), optional database filter.
 */

import { apiClient } from "../api-client";
import { AuthStore } from "../auth-store";

export interface LineageNode {
  id: number;
  name: string;
  schema_name: string;
  table_type: string;
  level: number;
}

export interface LineageEdgeColumnPair {
  referenced_column?: string;
  referencing_column?: string;
}

export interface LineageEdge {
  source: number;
  target: number;
  relationship_type: string;
  label?: string | null;
  column_mapping?: LineageEdgeColumnPair[] | null;
  cardinality?: string | null; // one_to_one, one_to_many, many_to_many
  is_join_table?: boolean | null;
}

export interface LineageFullGraphResponse {
  nodes: LineageNode[];
  edges: LineageEdge[];
}

export interface LineageGraphResponse extends LineageFullGraphResponse {
  root_table_id: number;
}

function getToken(): string | null {
  return AuthStore.getToken();
}

export async function getFullLineage(databaseId?: number): Promise<LineageFullGraphResponse> {
  const qs = databaseId != null ? `?database_id=${databaseId}` : "";
  return apiClient.get<LineageFullGraphResponse>(`/lineage${qs}`, getToken() ?? undefined);
}

export async function getTableLineage(tableId: number): Promise<LineageGraphResponse> {
  return apiClient.get<LineageGraphResponse>(
    `/tables/${tableId}/lineage`,
    getToken() ?? undefined
  );
}
