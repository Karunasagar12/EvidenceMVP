export interface Study {
  title: string;
  authors: string[];
  abstract: string;
  source: string;
  url: string;
  publication_date: string;
  journal: string;
  doi: string;
}

export interface SearchResponse {
  query: string;
  corrected_query: string;
  total_results: number;
  studies: Study[];
  summary: string;
  sources_queried: string[];
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchEvidence(
  query: string,
  maxResults: number = 10
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    max_results: String(maxResults),
  });

  const response = await fetch(`${API_BASE_URL}/api/search?${params}`);

  if (!response.ok) {
    throw new Error(`Search failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
