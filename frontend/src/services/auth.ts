import { AxiosError } from 'axios'
import { api } from './api'
import { clearAccessToken, setAccessToken } from './storage'
import type { ApiErrorResponse, AuthUser, LoginPayload, LoginResponse } from '../types/auth'

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/auth/login', payload, {
    skipUnauthorizedHandler: true,
  })
  setAccessToken(response.data.access_token)
  return response.data
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const response = await api.get<AuthUser>('/auth/me')
  return response.data
}

export function logout(): void {
  clearAccessToken()
}

export function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as ApiErrorResponse | undefined
    return apiError?.message ?? fallbackMessage
  }

  return fallbackMessage
}
