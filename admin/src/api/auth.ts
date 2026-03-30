import request from './index';
import type { ApiResponse } from '@/types';

export function login(phone: string, code: string) {
  return request.post<ApiResponse<{ access_token: string }>>('/auth/login', { phone, code });
}
