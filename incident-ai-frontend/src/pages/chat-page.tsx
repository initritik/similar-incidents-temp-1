import { useState, useEffect, useCallback } from "react";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { ChatInput } from "@/components/chat/ChatInput";
import type { ChatMessageProps } from "@/components/chat/ChatMessage";
import { IncidentsPanel } from "@/components/incidents/IncidentsPanel";
import { chatWithIncidents } from "@/services/incidentApi";
import type { ChatRequest, SimilarIncident } from "@/types/incident";
import {
  loadMessagesFromSession,
  saveMessagesToSession,
  clearChatStorage,
} from "@/lib/chatStorage";
import { Trash2 } from "lucide-react";

interface AssistantResponse {
  answerText: string;
  incidents:  SimilarIncident[];
}

interface ChatPageProps {
  sessionId:         string;
  onSessionUpdated?: () => void;
}

function AssistantContent({
  answerText,
  incidents,
}: {
  answerText: string;
  incidents:  SimilarIncident[];
}) {
  return (
    <div>
      <p className="text-sm leading-relaxed" style={{ color: "hsl(var(--rl-ink-200))" }}>
        {answerText}
      </p>
      {incidents && incidents.length > 0 && <IncidentsPanel incidents={incidents} />}
    </div>
  );
}

export function ChatPage({ sessionId, onSessionUpdated }: ChatPageProps) {
  const [messages,           setMessages]           = useState<ChatMessageProps[]>([]);
  const [assistantResponses, setAssistantResponses] = useState<AssistantResponse[]>([]);
  const [isLoading,          setIsLoading]          = useState(false);

  useEffect(() => {
    const stored = loadMessagesFromSession(sessionId);
    if (stored.length === 0) {
      setMessages([]);
      setAssistantResponses([]);
      return;
    }

    const reconstructed: ChatMessageProps[] = [];
    const responses: AssistantResponse[]    = [];

    stored.forEach((msg) => {
      if (msg.role === "user") {
        reconstructed.push({ role: "user", content: msg.content as string });
      } else {
        const data = msg.content as { answerText: string; incidents: SimilarIncident[] };
        responses.push({ answerText: data.answerText, incidents: data.incidents });
        reconstructed.push({
          role:    "assistant",
          content: (
            <AssistantContent
              answerText={data.answerText}
              incidents={data.incidents}
            />
          ),
        });
      }
    });

    setMessages(reconstructed);
    setAssistantResponses(responses);
  }, [sessionId]);

  const handleClearChat = () => {
    setMessages([]);
    setAssistantResponses([]);
    clearChatStorage();
    onSessionUpdated?.();
  };

  const handleSendMessage = useCallback(async (userMessage: string) => {
    const userMsg: ChatMessageProps = { role: "user", content: userMessage };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const request: ChatRequest = { user_query: userMessage, top_k: 5 };
      const response = await chatWithIncidents(request);

      const responseData: AssistantResponse = {
        answerText: response.answer,
        incidents:  response.results || [],
      };

      const assistantMessage: ChatMessageProps = {
        role:    "assistant",
        content: (
          <AssistantContent
            answerText={response.answer}
            incidents={response.results || []}
          />
        ),
      };

      const updatedMessages  = [...newMessages, assistantMessage];
      const updatedResponses = [...assistantResponses, responseData];

      setMessages(updatedMessages);
      setAssistantResponses(updatedResponses);

      saveMessagesToSession(sessionId, updatedMessages, updatedResponses);
      onSessionUpdated?.();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "An error occurred";
      console.error("Chat API error:", msg);

      setMessages((prev) => [
        ...prev,
        {
          role:    "assistant",
          content: (
            <div
              className="rounded-xl border px-4 py-3 text-sm"
              style={{
                background:  "hsl(350 70% 55% / 0.08)",
                borderColor: "hsl(350 70% 55% / 0.2)",
                color:       "hsl(350 70% 72%)",
              }}
            >
              <p className="font-semibold">Something went wrong</p>
              <p className="mt-1 text-xs opacity-80">{msg}</p>
            </div>
          ),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, assistantResponses, sessionId, onSessionUpdated]);

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* ── Toolbar ── */}
      <div
        className="flex items-center h-16 justify-between pl-12 pr-4 sm:pl-14 sm:pr-6 lg:px-12 py-3.5"
        style={{
          borderBottom:   "1px solid hsl(var(--rl-ink-800))",
          background:     "hsl(var(--rl-ink-950) / 0.85)",
          backdropFilter: "blur(8px)",
        }}
      >
        <div className="flex items-center gap-2.5">
          {/* <div
            className="h-1.5 w-1.5 rounded-full"
            style={{
              background: "hsl(var(--rl-gold-400))",
              boxShadow:  "0 0 6px hsl(var(--rl-gold-400) / 0.55)",
            }}
          />
          <p
            className="text-[10px] font-semibold uppercase tracking-[0.14em]"
            style={{ color: "hsl(var(--rl-ink-400))" }}
          >
            Conversation
          </p> */}
        </div>

        <button
          onClick={handleClearChat}
          disabled={messages.length === 0}
          className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-30"
          style={{ color: "hsl(var(--rl-ink-500))" }}
          onMouseEnter={(e) => {
            if (!((e.currentTarget as HTMLButtonElement).disabled)) {
              (e.currentTarget as HTMLButtonElement).style.background =
                "hsl(var(--rl-ink-800))";
              (e.currentTarget as HTMLButtonElement).style.color =
                "hsl(var(--rl-ink-200))";
            }
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = "transparent";
            (e.currentTarget as HTMLButtonElement).style.color =
              "hsl(var(--rl-ink-500))";
          }}
        >
          <Trash2 size={12} strokeWidth={2} />
          Clear
        </button>
      </div>

      {/* ── Messages ── */}
      <ChatContainer
        messages={messages}
        isLoading={isLoading}
        onSuggestionClick={handleSendMessage}
      />

      {/* ── Input ── */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}