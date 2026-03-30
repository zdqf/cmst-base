import request from './index';
import type { ApiResponse, PaginatedData, ComplianceWord, ComplianceWordCreateRequest, ComplianceWordUpdateRequest } from '@/types';

export function getComplianceWords(params: { page: number; page_size: number }) {
  return request.get<ApiResponse<PaginatedData<ComplianceWord>>>('/admin/compliance', { params });
}

export function createComplianceWord(data: ComplianceWordCreateRequest) {
  return request.post<ApiResponse<ComplianceWord>>('/admin/compliance', data);
}

export function updateComplianceWord(id: string, data: ComplianceWordUpdateRequest) {
  return request.put<ApiResponse<ComplianceWord>>(`/admin/compliance/${id}`, data);
}

export function deleteComplianceWord(id: string) {
  return request.delete<ApiResponse>(`/admin/compliance/${id}`);
}
