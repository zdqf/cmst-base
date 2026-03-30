import request from './index';
import type { ApiResponse, PaginatedData, AdminConsultationItem } from '@/types';

export function getConsultations(params: { page: number; page_size: number; status?: string }) {
  return request.get<ApiResponse<PaginatedData<AdminConsultationItem>>>('/admin/consultations', { params });
}

export function updateConsultationStatus(id: string, status: string) {
  return request.put<ApiResponse>(`/admin/consultations/${id}/status`, { status });
}

export function updateConsultationNotes(id: string, admin_notes: string) {
  return request.put<ApiResponse>(`/admin/consultations/${id}/notes`, { admin_notes });
}
