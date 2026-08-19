import { StatusPanel } from '../components/StatusPanel'

export function HomePage() {
  return (
    <main>
      <header className="masthead">
        <a className="brand" href="/" aria-label="Book Pilots home">
          <span className="brand-mark">BP</span>
          <span>Book Pilots</span>
        </a>
        <span className="edition">Foundation build · 001</span>
      </header>

      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Read together, thoughtfully</p>
        <h1 id="page-title">Your next chapter starts with good company.</h1>
        <p className="intro">
          The foundation for recommendations, shared reading, and book club
          conversations is ready.
        </p>
      </section>

      <StatusPanel />
    </main>
  )
}