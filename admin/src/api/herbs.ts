import request from './index';
import type { ApiResponse, PaginatedData, HerbDetail, HerbCreateRequest, HerbUpdateRequest } from '@/types';

export function getHerbs(params: { page: number; page_size: number; category?: string; keyword?: string; status?: string }) {
  return request.get<ApiResponse<PaginatedData<HerbDetail>>>('/admin/herbs', { params });
}

export function createHerb(data: HerbCreateRequest) {
  return request.post<ApiResponse<HerbDetail>>('/admin/herbs', data);
}

export function updateHerb(id: string, data: HerbUpdateRequest) {
  return request.put<ApiResponse<HerbDetail>>(`/admin/herbs/${id}`, data);
}

export function updateHerbStatus(id: string, status: string) {
  return request.put<ApiResponse>(`/admin/herbs/${id}/status`, { status });
}

export function generateHerbContent(id: string) {
  return request.post<ApiResponse<{ content: string }>>(`/admin/herbs/${id}/generate-content`);
}
