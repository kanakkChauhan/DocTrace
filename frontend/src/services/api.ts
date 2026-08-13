const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export interface DocumentResponse {
  id: string;
  title: string;
  content: string;
  version: string;
  created_at: string;
}

export interface DocumentCreatePayload {
  title: string;
  content: string;
  version?: string;
}

export async function fetchDocuments(): Promise<DocumentResponse[]> {
  const response = await fetch(`${API_BASE_URL}/documents/`);
  if (!response.ok) {
    throw new Error("Failed to fetch documents from server");
  }
  return response.json();
}

export async function createDocument(payload: DocumentCreatePayload): Promise<DocumentResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create document");
  }
  return response.json();
}

export interface ClaimResponse {
    id: string;
    document_id: string;
    statement: string;
    section: string | null;
  }
  
  export async function extractClaims(documentId: string): Promise<ClaimResponse[]> {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/extract`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new Error("Failed to extract claims");
    }
    return response.json();
  }