import { MessageSquareReply, Plus } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { createDiscussion, createDiscussionPost, getDiscussions } from "../api/communication";
import { useAuth } from "../context/AuthContext";
import type { DiscussionThread } from "../types/communication";

export function ClubDiscussions({ clubId }: { clubId: number }) {
  const { user } = useAuth();
  const [threads, setThreads] = useState<DiscussionThread[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [error, setError] = useState("");
  async function refresh() { const items = await getDiscussions(clubId); setThreads(items); setSelectedId((current) => current ?? items[0]?.id ?? null); }
  useEffect(() => {
    getDiscussions(clubId).then((items) => {
      setThreads(items);
      setSelectedId(items[0]?.id ?? null);
    });
  }, [clubId]);
  async function newThread() { const title = prompt("Discussion title"); if (!title?.trim()) return; try { const thread = await createDiscussion(clubId, title); setThreads((items) => [thread, ...items]); setSelectedId(thread.id); } catch { setError("A current club book is required before starting a discussion."); } }
  async function post(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!selectedId) return; const form = new FormData(event.currentTarget); await createDiscussionPost(clubId, selectedId, String(form.get("post")), replyTo); event.currentTarget.reset(); setReplyTo(null); await refresh(); }
  const selected = threads.find((thread) => thread.id === selectedId);
  const roots = selected?.posts.filter((post) => !post.parent_id) ?? [];
  return (
    <section className="discussion-pane">
      <aside className="thread-list"><button className="new-thread" type="button" onClick={newThread}><Plus size={17} /> New thread</button>{threads.map((thread) => <button className={thread.id === selectedId ? "active" : ""} type="button" key={thread.id} onClick={() => setSelectedId(thread.id)}><strong>{thread.title}</strong><span>{thread.posts.length} posts · {thread.book.title}</span></button>)}</aside>
      <div className="thread-content">{selected ? <><p className="kicker">{selected.book.title}</p><h2>{selected.title}</h2><div className="discussion-posts">{roots.map((post) => <article key={post.id}><div><strong>{post.author.first_name} {post.author.last_name}</strong><time>{new Date(post.created_at).toLocaleString()}</time></div><p>{post.content}</p><button type="button" onClick={() => setReplyTo(post.id)}><MessageSquareReply size={15} /> Reply</button>{selected.posts.filter((reply) => reply.parent_id === post.id).map((reply) => <article className="nested-reply" key={reply.id}><strong>{reply.author.first_name} {reply.author.last_name}{reply.author_id === user?.id ? " · you" : ""}</strong><p>{reply.content}</p></article>)}</article>)}</div><form className="discussion-composer" onSubmit={post}><label>{replyTo ? "Write a reply" : "Add to the discussion"}<textarea name="post" required maxLength={5000} /></label><button className="form-submit" type="submit">Post</button></form></> : <p>Start a thread for the club’s current book.</p>}{error ? <p role="alert" className="form-error">{error}</p> : null}</div>
    </section>
  );
}