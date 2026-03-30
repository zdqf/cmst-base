import request from './index';
import type { ApiResponse, PaginatedData, AdminOrderItem } from '@/types';

export function getOrders(params: { page: number; page_size: number; status?: string; start_date?: string; end_date?: string }) {
  return request.get<ApiResponse<PaginatedData<AdminOrderItem>>>('/admin/orders', { params });
}

export function updateOrderStatus(id: string, status: string) {
  return request.put<ApiResponse>(`/admin/orders/${id}/status`, { status });
}
