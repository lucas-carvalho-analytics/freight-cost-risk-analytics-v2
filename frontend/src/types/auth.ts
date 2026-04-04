export interface LoginPayload {
  email: string
  password: string
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface AuthUser {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

export interface ApiErrorResponse {
  error: string
  message: string
  status_code: number
  details?: unknown
}
