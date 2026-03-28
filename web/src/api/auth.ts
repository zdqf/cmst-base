import client from './client'
import type { AuthResponse } from '../types'

export function login(phone: string, code: string): Promise<AuthResponse> {
  return client.post('/api/v1/auth/login', { phone, code })
}

export function register(phone: string, code: string): Promise<AuthResponse> {
  return client.post('/api/v1/auth/register', { phone, code })
}
