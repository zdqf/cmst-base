import request from './index';
import type { ApiResponse, PaginatedData, PromptTemplate, PromptUpdateRequest, PromptTestRequest, PromptTestResponse } from '@/types';

export function getPrompts(params: { page: number; page_size: number; type?: string }) {
  return request.get<ApiResponse<PaginatedData<PromptTemplate>>>('/admin/prompts', { params });
}

export function getActivePrompt(type: string) {
  return request.get<ApiResponse<PromptTemplate>>(`/admin/prompts/${type}/active`);
}

export function updatePrompt(type: string, data: PromptUpdateRequest) {
  return request.put<ApiResponse<PromptTemplate>>(`/admin/prompts/${type}`, data);
}

export function getPromptHistory(type: string, params: { page: number; page_size: number }) {
  return request.get<ApiResponse<PaginatedData<PromptTemplate>>>(`/admin/prompts/${type}/history`, { params });
}

export function testPrompt(data: PromptTestRequest) {
  return request.post<ApiResponse<PromptTestResponse>>('/admin/prompts/test', data);
}
