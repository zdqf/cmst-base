import request from './index';
import type { ApiResponse, PaginatedData, AdminUserItem } from '@/types';

export function getUsers(params: { page: number; page_size: number; phone?: string }) {
  return request.get<ApiResponse<PaginatedData<AdminUserItem>>>('/admin/users', { params });
}

export function disableUser(id: string) {
  return request.put<ApiResponse>(`/admin/users/${id}/disable`);
}
