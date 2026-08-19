import { ArrowRight, CircleAlert, Database, Sparkles } from "lucide-react";

import { useHealth } from "../hooks/useHealth";

export function HomePage() {
  const health = useHealth();

  return (
    <section className="home">
      <div className="intro">
        <p className="kicker">A better reading orbit</p>
        <h1>Find the book that moves your club forward.</h1>
        <p className="lede">
          Thoughtful recommendations, shared reading rooms, and conversations that stay with you.
        </p>
        <button className="primary-action" type="button" disabled>
          Recommendations coming soon <ArrowRight aria-hidden="true" size={18} />
        </button>
      </div>

      <div className="shelf-scene" aria-hidden="true">
        <div className="book book-coral" />
        <div className="book book-ink" />
        <div className="book book-gold" />
        <Sparkles className="spark" size={32} strokeWidth={1.4} />
      </div>

      <div className={`system-status status-${health.kind}`} aria-live="polite">
        {health.kind === "ready" ? <Database aria-hidden="true" size={20} /> : null}
        {health.kind === "error" ? <CircleAlert aria-hidden="true" size={20} /> : null}
        <div>
          <strong>
            {health.kind === "loading" && "Checking system"}
            {health.kind === "ready" && "All systems ready"}
            {health.kind === "error" && "Backend unavailable"}
          </strong>
          <span>
            {health.kind === "ready"
              ? `API healthy · Database ${health.health.database}`
              : "FastAPI and PostgreSQL status"}
          </span>
        </div>
      </div>
    </section>
  );
}