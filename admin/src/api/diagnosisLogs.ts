import request from './index';
import type { ApiResponse, PaginatedData, AdminDiagnosisLogItem } from '@/types';

export function getDiagnosisLogs(params: { page: number; page_size: number; user_id?: string; start_date?: string; end_date?: string }) {
  return request.get<ApiResponse<PaginatedData<AdminDiagnosisLogItem>>>('/admin/diagnosis-logs', { params });
}

export function getDiagnosisLogDetail(id: string) {
  return request.get<ApiResponse<AdminDiagnosisLogItem>>(`/admin/diagnosis-logs/${id}`);
}
