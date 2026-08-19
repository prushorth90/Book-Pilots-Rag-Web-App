import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import { getClub } from "../api/clubs";
import { ClubChat } from "../components/ClubChat";
import { ClubDiscussions } from "../components/ClubDiscussions";
import type { ClubDetail } from "../types/clubs";

export function ClubCommunicationPage() {
  const { clubId = "" } = useParams(); const id = Number(clubId);
  const [params, setParams] = useSearchParams();
  const [club, setClub] = useState<ClubDetail | null>(null);
  const tab = params.get("tab") === "discussion" ? "discussion" : "chat";
  useEffect(() => { getClub(id).then(setClub); }, [id]);
  if (!club) return <p className="route-loading">Loading club communication...</p>;
  if (!club.viewer_role) return <p className="route-loading">Join this club to participate.</p>;
  return (
    <section className="communication-page">
      <header><div><p className="kicker">{club.name}</p><h1>Club room.</h1></div><Link to={`/clubs/${id}`}>Back to club</Link></header>
      <div className="communication-tabs" role="tablist"><button role="tab" aria-selected={tab === "chat"} onClick={() => setParams({ tab: "chat" })}>Live chat</button><button role="tab" aria-selected={tab === "discussion"} onClick={() => setParams({ tab: "discussion" })}>Book discussion</button></div>
      {tab === "chat" ? <ClubChat clubId={id} viewerRole={club.viewer_role} /> : <ClubDiscussions clubId={id} />}
    </section>
  );
}