import { Pencil, Send, ShieldX, Trash2 } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";

import { deleteMessage, editMessage, moderateMessage } from "../api/communication";
import { useAuth } from "../context/AuthContext";
import { useClubChat } from "../hooks/useClubChat";
import type { ClubRole } from "../types/clubs";

export function ClubChat({ clubId, viewerRole }: { clubId: number; viewerRole: ClubRole }) {
  const { user } = useAuth();
  const { messages, setMessages, status, send } = useClubChat(clubId);
  const [error, setError] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const canModerate = ["OWNER", "ADMIN", "MODERATOR"].includes(viewerRole);
  useEffect(() => {
    if (typeof endRef.current?.scrollIntoView === "function") {
      endRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget); const content = String(form.get("message")).trim();
    if (!content) return;
    if (send(content)) { event.currentTarget.reset(); setError(""); } else setError("Chat is reconnecting. Your message was not sent yet.");
  }
  async function edit(id: number, current: string) {
    const content = prompt("Edit message", current); if (!content?.trim()) return;
    const updated = await editMessage(clubId, id, content); setMessages((items) => items.map((item) => item.id === id ? updated : item));
  }
  async function remove(id: number, moderate: boolean) {
    const updated = moderate ? await moderateMessage(clubId, id) : (await deleteMessage(clubId, id), null);
    setMessages((items) => items.map((item) => item.id === id ? updated ?? { ...item, content: "Message removed", is_deleted: true } : item));
  }
  return (
    <section className="club-chat-pane">
      <div className="chat-status"><span className={`connection-dot status-${status}`} />{status}</div>
      <div className="message-history" aria-live="polite">{messages.map((message) => <article className={`chat-message ${message.sender_id === user?.id ? "own-message" : ""}`} key={message.id}>
        <div className="message-heading"><strong>{message.sender.first_name} {message.sender.last_name}</strong><time>{new Date(message.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</time></div>
        <p>{message.content}</p>{message.edited_at && !message.is_deleted ? <span className="edited-label">edited</span> : null}
        {!message.is_deleted ? <div className="message-actions">{message.sender_id === user?.id ? <><button type="button" title="Edit message" onClick={() => edit(message.id, message.content)}><Pencil size={15} /></button><button type="button" title="Delete message" onClick={() => remove(message.id, false)}><Trash2 size={15} /></button></> : null}{canModerate && message.sender_id !== user?.id ? <button type="button" title="Remove as moderator" onClick={() => remove(message.id, true)}><ShieldX size={15} /></button> : null}</div> : null}
      </article>)}<div ref={endRef} /></div>
      <form className="chat-composer" onSubmit={submit}><input name="message" aria-label="Message" maxLength={5000} autoComplete="off" placeholder="Write to the club" /><button type="submit" aria-label="Send message"><Send size={19} /></button></form>
      {error ? <p className="form-error" role="alert">{error}</p> : null}
    </section>
  );
}