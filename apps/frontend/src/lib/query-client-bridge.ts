import type { QueryClient } from '@tanstack/react-query'

let browserQueryClient: QueryClient | null = null

/** Registers the browser QueryClient so non-React modules (e.g. fetch helpers) can invalidate caches. */
export function setBrowserQueryClient(client: QueryClient | null) {
  browserQueryClient = client
}

export function getBrowserQueryClient(): QueryClient | null {
  return browserQueryClient
}
