const configuredBase = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const API_BASE = `${configuredBase}/api/v1`;

export interface DocumentResponse {
  id: string;
  title: string;
  content: string;
  version: string;
  created_at: string;
}

export interface ClaimResponse {
  id: string;
  document_id: string;
  statement: string;
  section: string | null;
}

export interface CodeLocation {
  line: number;
  end_line: number | null;
}

export interface TraceLinkResponse {
  id?: string;
  claim_id: string;
  code_element_type: string;
  code_element_name: string;
  filepath: string;
  location: CodeLocation;
  match_type: string;
  match_score: number;
  evidence: string[];
  status: string;
}

export interface TraceStateResponse {
  document_id: string;
  total_claims: number;
  total_matches: number;
  claims: ClaimResponse[];
  links: TraceLinkResponse[];
}

export interface ComplianceMetrics {
  document_id: string;
  document_title: string;
  total_claims: number;
  traced_claims: number;
  untraced_claims: number;
  verified_claims: number;
  rejected_claims: number;
  pending_claims: number;
  total_links: number;
  strong_matches: number;
  weak_matches: number;
  compliance_percentage: number;
  coverage_percentage: number;
}

/**
 * Shared fetch wrapper. Surfaces the backend's own error `detail` message
 * when available (so users see e.g. "GROQ_API_KEY is missing" instead of a
 * generic "Failed to ..." string), and turns network failures into a clear,
 * human-readable message instead of letting a raw TypeError bubble up.
 */
async function request<T>(
  url: string,
  options: RequestInit,
  fallbackMessage: string
): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, options);
  } catch {
    throw new Error(
      "Could not reach the DocTrace API. Check your network connection and that the backend is running."
    );
  }

  if (!res.ok) {
    let detail: string | undefined;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Response body wasn't JSON (or was empty) -- fall back below.
    }
    throw new Error(detail || fallbackMessage);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export async function fetchDocuments(): Promise<DocumentResponse[]> {
  return request<DocumentResponse[]>(
    `${API_BASE}/documents/`,
    {},
    "Failed to fetch documents"
  );
}

export async function createDocument(data: {
  title: string;
  content: string;
  version: string;
}): Promise<DocumentResponse> {
  return request<DocumentResponse>(
    `${API_BASE}/documents/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    },
    "Failed to create document"
  );
}

export async function deleteDocument(id: string): Promise<void> {
  await request<void>(
    `${API_BASE}/documents/${id}`,
    { method: "DELETE" },
    "Failed to delete document"
  );
}

export async function extractClaims(documentId: string): Promise<ClaimResponse[]> {
  return request<ClaimResponse[]>(
    `${API_BASE}/documents/${documentId}/extract`,
    { method: "POST" },
    "Failed to extract claims"
  );
}

export async function runTraceability(
  documentId: string,
  payload: { files?: { filepath: string; source_code: string }[]; github_url?: string }
): Promise<TraceStateResponse> {
  // Backend requires document_id in the body
  const reqPayload = { document_id: documentId, ...payload };
  return request<TraceStateResponse>(
    `${API_BASE}/trace/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reqPayload),
    },
    "Failed to run traceability"
  );
}

export async function fetchTraceState(documentId: string): Promise<TraceStateResponse> {
  return request<TraceStateResponse>(
    `${API_BASE}/trace/${documentId}`,
    {},
    "Failed to fetch trace state"
  );
}

export async function fetchComplianceMetrics(
  documentId: string
): Promise<ComplianceMetrics> {
  return request<ComplianceMetrics>(
    `${API_BASE}/compliance/${documentId}`,
    {},
    "Failed to fetch compliance metrics"
  );
}

export async function updateLinkStatus(
  linkId: string,
  status: "pending" | "verified" | "rejected"
): Promise<{ status: string; link_id: string; new_status: string }> {
  return request<{ status: string; link_id: string; new_status: string }>(
    `${API_BASE}/trace/links/${linkId}/status`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    },
    "Failed to update link status"
  );
}