import request from './index';

export interface DashboardStats {
  users: number;
  orders: number;
  pending_orders: number;
  consultations: number;
  pending_consultations: number;
  products: number;
  herbs: number;
  diagnosis_logs: number;
}

export function getDashboardStats() {
  return request.get<{ data: DashboardStats }>('/admin/dashboard/stats');
}
