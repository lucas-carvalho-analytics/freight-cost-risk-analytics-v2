import axios from 'axios'
import { clearAccessToken, getAccessToken } from './storage'

declare module 'axios' {
  export interface AxiosRequestConfig {
    skipUnauthorizedHandler?: boolean
  }
}

let unauthorizedHandler: (() => void) | null = null

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const statusCode = error.response?.status
    const shouldHandleUnauthorized =
      statusCode === 401 && !error.config?.skipUnauthorizedHandler

    if (shouldHandleUnauthorized) {
      clearAccessToken()
      unauthorizedHandler?.()
    }

    return Promise.reject(error)
  },
)
