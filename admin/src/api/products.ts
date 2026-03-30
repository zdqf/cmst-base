import request from './index';
import type { ApiResponse, PaginatedData, ProductDetail, ProductCreateRequest, ProductUpdateRequest, ProductStockUpdateRequest } from '@/types';

export function getProducts(params: { page: number; page_size: number; category?: string; status?: string }) {
  return request.get<ApiResponse<PaginatedData<ProductDetail>>>('/admin/products', { params });
}

export function createProduct(data: ProductCreateRequest) {
  return request.post<ApiResponse<ProductDetail>>('/admin/products', data);
}

export function updateProduct(id: string, data: ProductUpdateRequest) {
  return request.put<ApiResponse<ProductDetail>>(`/admin/products/${id}`, data);
}

export function updateProductStatus(id: string, status: string) {
  return request.put<ApiResponse>(`/admin/products/${id}/status`, { status });
}

export function updateProductStock(id: string, data: ProductStockUpdateRequest) {
  return request.put<ApiResponse>(`/admin/products/${id}/stock`, data);
}
