import { useEffect, useState } from 'react'

import { getHealth } from '../api/health'
import type { HealthResponse } from '../types/health'

type LoadState =
  | { kind: 'loading' }
  | { kind: 'ready'; health: HealthResponse }
  | { kind: 'error' }

export function StatusPanel() {
  const [state, setState] = useState<LoadState>({ kind: 'loading' })

  useEffect(() => {
    const controller = new AbortController()

    void getHealth(controller.signal)
      .then((health) => setState({ kind: 'ready', health }))
      .catch(() => {
        if (!controller.signal.aborted) setState({ kind: 'error' })
      })

    return () => controller.abort()
  }, [])

  return (
    <section className="status" aria-live="polite">
      <div>
        <p className="status-label">System status</p>
        <h2>{statusHeading(state)}</h2>
      </div>
      <span className={`indicator indicator--${state.kind}`} aria-hidden="true" />
    </section>
  )
}

function statusHeading(state: LoadState) {
  if (state.kind === 'ready') {
    return state.health.database === 'ok'
      ? 'API and library database connected'
      : 'API connected'
  }
  if (state.kind === 'error') return 'Connection unavailable'
  return 'Checking connections'
}