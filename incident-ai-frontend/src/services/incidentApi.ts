import type {
  ChatRequest,
  ChatResponse,
  SearchIncidentsRequest,
  SearchIncidentsResponse,
} from "@/types/incident";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "https://incident-ai-backend-4o8d.onrender.com";


type ApiErrorPayload = {
  detail?: string;
  message?: string;
};


async function parseJsonResponse<T>(response: Response): Promise<T> {
  let payload: unknown;

  try {
    payload = await response.json();
  } catch {
    throw new Error("Backend returned an invalid JSON response.");
  }

  if (!response.ok) {
    const errorPayload = payload as ApiErrorPayload;
    throw new Error(
      errorPayload.detail ??
        errorPayload.message ??
        `Backend request failed with status ${response.status}.`,
    );
  }

  return payload as T;
}


async function postJson<TResponse, TRequest>(
  path: string,
  body: TRequest,
): Promise<TResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    return parseJsonResponse<TResponse>(response);
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }

    throw new Error("Network request failed.");
  }
}


function validateSearchResponse(
  response: SearchIncidentsResponse,
): SearchIncidentsResponse {
  if (!response || !Array.isArray(response.results)) {
    throw new Error("Invalid search response from backend.");
  }

  return response;
}


function validateChatResponse(response: ChatResponse): ChatResponse {
  if (!response || typeof response.answer !== "string" || !Array.isArray(response.results)) {
    throw new Error("Invalid chat response from backend.");
  }

  return response;
}


// API logic is separated from UI components so pages can focus on rendering and
// interaction. Centralizing backend calls also keeps error handling, base URLs,
// and response validation consistent across the app.
export async function searchIncidents(
  request: SearchIncidentsRequest,
): Promise<SearchIncidentsResponse> {
  const response = await postJson<SearchIncidentsResponse, SearchIncidentsRequest>(
    "/search/similar-incidents",
    request,
  );

  return validateSearchResponse(response);
}


// This wrapper will later power the chat UI without forcing components to know
// endpoint paths, request details, or backend response quirks.
export async function chatWithIncidents(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await postJson<ChatResponse, ChatRequest>(
    "/chat/incidents",
    request,
  );

  return validateChatResponse(response);
}
