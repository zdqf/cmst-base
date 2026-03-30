// ============================================================
// 草木沈塘 管理后台 — 类型定义（与后端 Schema 完全对齐）
// ============================================================

// --- 通用 ---
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page: number;
  page_size: number;
}

// --- 用户 ---
export interface AdminUserItem {
  id: string;
  phone: string;
  nickname: string | null;
  status: string;
  is_admin: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

// --- 中药 ---
export interface HerbDetail {
  id: string;
  name: string;
  category: string | null;
  origin_and_form: string | null;
  flavor_meridian: string | null;
  common_pairings: string | null;
  unsuitable_groups: string | null;
  precautions: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface HerbCreateRequest {
  name: string;
  category?: string;
  origin_and_form?: string;
  flavor_meridian?: string;
  common_pairings?: string;
  unsuitable_groups?: string;
  precautions?: string;
}

export interface HerbUpdateRequest extends Partial<HerbCreateRequest> {}

// --- 商品 ---
export interface ProductDetail {
  id: string;
  name: string;
  category: string | null;
  price: number;
  specification: string | null;
  description: string | null;
  image_url: string | null;
  stock: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProductCreateRequest {
  name: string;
  category?: string;
  price: number;
  specification?: string;
  description?: string;
  image_url?: string;
  stock?: number;
}

export interface ProductUpdateRequest {
  name?: string;
  category?: string;
  price?: number;
  specification?: string;
  description?: string;
  image_url?: string;
}

export interface ProductStockUpdateRequest {
  change_amount: number;
  reason: string;
}

// --- 订单 ---
export interface AdminOrderItem {
  id: string;
  order_no: string;
  user_id: string;
  total_amount: number;
  status: string;
  created_at: string;
  updated_at: string;
}

// --- 咨询 ---
export interface AdminConsultationItem {
  id: string;
  user_id: string;
  name: string;
  contact: string;
  subject: string;
  description: string;
  status: string;
  admin_notes: string | null;
  handled_by: string | null;
  handled_at: string | null;
  created_at: string;
  updated_at: string;
}

// --- 问诊记录 ---
export interface AdminDiagnosisLogItem {
  id: string;
  user_id: string;
  input_data: Record<string, any>;
  ai_output: string;
  prompt_version: string | null;
  created_at: string;
  updated_at: string;
}

// --- Prompt 模板 ---
export interface PromptTemplate {
  id: string;
  type: string;
  role_name: string;
  content: string;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PromptUpdateRequest {
  content: string;
  role_name?: string;
}

export interface PromptTestRequest {
  type: string;
  test_input: string;
}

export interface PromptTestResponse {
  type: string;
  test_input: string;
  ai_output: string;
}

// --- 合规 ---
export interface ComplianceWord {
  id: string;
  forbidden_word: string;
  replacement: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComplianceWordCreateRequest {
  forbidden_word: string;
  replacement?: string;
}

export interface ComplianceWordUpdateRequest {
  forbidden_word?: string;
  replacement?: string;
}
