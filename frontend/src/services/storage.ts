const TOKEN_KEY = 'freight_cost_risk_analytics_token'

export function getAccessToken(): string | null {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setAccessToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearAccessToken(): void {
  window.localStorage.removeItem(TOKEN_KEY)
}
