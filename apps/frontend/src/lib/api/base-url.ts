function stripTrailingSlash(value: string) {
  return value.endsWith('/') ? value.slice(0, -1) : value
}

function isLocalBrowserHost(hostname: string) {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0'
}

export function getApiBaseUrl() {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return stripTrailingSlash(process.env.NEXT_PUBLIC_API_URL)
  }

  if (typeof window !== 'undefined') {
    if (isLocalBrowserHost(window.location.hostname)) {
      const port = window.location.port
      // Default HTTP/HTTPS ports: same origin as the page (e.g. Caddy on :443 / :80 proxies /api).
      if (!port || port === '80' || port === '443') {
        return stripTrailingSlash(window.location.origin)
      }
      // Dedicated API origin (e.g. FastAPI on :8000).
      if (port === '8000') {
        return stripTrailingSlash(window.location.origin)
      }
      // Typical Next.js dev (e.g. :3000) talks to the API on :8000.
      return `${window.location.protocol}//${window.location.hostname}:8000`
    }
    return stripTrailingSlash(window.location.origin)
  }

  return 'http://localhost:8000'
}
