import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'

import { StatusPanel } from './StatusPanel'

afterEach(() => vi.restoreAllMocks())

test('shows connected services after a successful health check', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify({ status: 'ok', database: 'ok' }), {
      status: 200,
    }),
  )

  render(<StatusPanel />)

  expect(
    await screen.findByText('API and library database connected'),
  ).toBeInTheDocument()
})