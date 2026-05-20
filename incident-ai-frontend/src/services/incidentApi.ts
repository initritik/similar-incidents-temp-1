import type {
  AgentProgressEvent,
  ChatRequest,
  ChatResponse,
  SearchIncidentsRequest,
  SearchIncidentsResponse,
} from "@/types/incident";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "https://incident-ai-backend-4o8d.onrender.com";

type ApiErrorPayload = { detail?: string; message?: string };

async function parseJsonResponse<T>(response: Response): Promise<T> {
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Backend returned an invalid JSON response.");
  }
  if (!response.ok) {
    const err = payload as ApiErrorPayload;
    throw new Error(
      err.detail ?? err.message ?? `Backend request failed with status ${response.status}.`
    );
  }
  return payload as T;
}

async function postJson<TResponse, TRequest>(
  path: string,
  body: TRequest
): Promise<TResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return parseJsonResponse<TResponse>(response);
  } catch (error) {
    if (error instanceof Error) throw error;
    throw new Error("Network request failed.");
  }
}

export async function searchIncidents(
  request: SearchIncidentsRequest
): Promise<SearchIncidentsResponse> {
  const response = await postJson<SearchIncidentsResponse, SearchIncidentsRequest>(
    "/search/similar-incidents",
    request
  );
  if (!response || !Array.isArray(response.results)) {
    throw new Error("Invalid search response from backend.");
  }
  return response;
}

/**
 * Chat with incidents via SSE streaming.
 *
 * Calls onProgress for each agent step event.
 * Resolves with the final ChatResponse when the 'result' event arrives.
 * Rejects on 'error' events or network failure.
 */
export function chatWithIncidentsStream(
  request: ChatRequest,
  onProgress: (event: AgentProgressEvent) => void
): Promise<ChatResponse> {
  return new Promise((resolve, reject) => {
    fetch(`${API_BASE_URL}/chat/incidents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    })
      .then((response) => {
        if (!response.ok || !response.body) {
          return response.json().then((err: ApiErrorPayload) => {
            reject(new Error(err.detail ?? err.message ?? `HTTP ${response.status}`));
          });
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        function parseSseChunk(chunk: string) {
          // SSE messages end with \n\n; each line is "field: value"
          const messages = (buffer + chunk).split("\n\n");
          buffer = messages.pop() ?? "";

          for (const msg of messages) {
            let eventType = "message";
            let dataLine = "";

            for (const line of msg.split("\n")) {
              if (line.startsWith("event: ")) eventType = line.slice(7).trim();
              if (line.startsWith("data: "))  dataLine  = line.slice(6).trim();
            }

            if (!dataLine) continue;

            try {
              const parsed = JSON.parse(dataLine);
              if (eventType === "progress") {
                onProgress(parsed as AgentProgressEvent);
              } else if (eventType === "result") {
                resolve(parsed as ChatResponse);
              } else if (eventType === "error") {
                reject(new Error((parsed as { message: string }).message));
              }
            } catch {
              // Malformed SSE data — ignore
            }
          }
        }

        function pump(): Promise<void> {
          return reader.read().then(({ done, value }) => {
            if (done) return;
            parseSseChunk(decoder.decode(value, { stream: true }));
            return pump();
          });
        }

        pump().catch(reject);
      })
      .catch(reject);
  });
}

/** Legacy non-streaming chat — kept for backwards compat with search page. */
export async function chatWithIncidents(request: ChatRequest): Promise<ChatResponse> {
  return new Promise((resolve, reject) => {
    chatWithIncidentsStream(request, () => {}).then(resolve).catch(reject);
  });
}