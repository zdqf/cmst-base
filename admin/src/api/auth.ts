import request from './index';
import type { ApiResponse } from '@/types';

export function login(phone: string, code: string) {
  return request.post<ApiResponse<{ access_token: string }>>('/auth/login', { phone, code });
}

export function sendSmsCode(phone: string) {
  return request.post<ApiResponse>('/auth/sms/send', { phone });
}

export function adminLogin(phone: string, password: string) {
  return request.post<ApiResponse<{ access_token: string }>>('/auth/admin/login', { phone, password });
}
