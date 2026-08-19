import { useEffect, useRef, useState } from "react";

import { clubChatUrl, getMessageHistory } from "../api/communication";
import type { ChatMessage } from "../types/communication";

type ConnectionStatus = "connecting" | "connected" | "reconnecting" | "offline";

export function useClubChat(clubId: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let active = true;
    let reconnectTimer: number | undefined;
    let attempts = 0;
    getMessageHistory(clubId).then((history) => active && setMessages(history));

    function connect() {
      if (!active) return;
      setStatus(attempts ? "reconnecting" : "connecting");
      const socket = new WebSocket(clubChatUrl(clubId));
      socketRef.current = socket;
      socket.onopen = () => { attempts = 0; setStatus("connected"); };
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data) as { type: string; message?: ChatMessage };
        if (!payload.message) return;
        setMessages((current) => {
          const found = current.some((message) => message.id === payload.message?.id);
          return found
            ? current.map((message) => message.id === payload.message?.id ? payload.message! : message)
            : [...current, payload.message!];
        });
      };
      socket.onclose = () => {
        if (!active) return;
        attempts += 1;
        setStatus(attempts > 5 ? "offline" : "reconnecting");
        reconnectTimer = window.setTimeout(connect, Math.min(1000 * 2 ** attempts, 15000));
      };
    }
    connect();
    return () => {
      active = false;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      socketRef.current?.close();
    };
  }, [clubId]);

  function send(content: string): boolean {
    if (socketRef.current?.readyState !== WebSocket.OPEN) return false;
    socketRef.current.send(JSON.stringify({ content }));
    return true;
  }

  return { messages, setMessages, status, send };
}