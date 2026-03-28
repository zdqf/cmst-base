// ===== 通用 =====
export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// ===== 认证 =====
export interface LoginRequest {
  phone: string
  code: string
}

export interface RegisterRequest {
  phone: string
  code: string
}

export interface AuthResponse {
  access_token: string
}

// ===== 中药 =====
export interface HerbListItem {
  id: string
  name: string
  category: string | null
  status: string
}

export interface HerbDetail {
  id: string
  name: string
  category: string | null
  origin_and_form: string | null
  flavor_meridian: string | null
  common_pairings: string | null
  unsuitable_groups: string | null
  precautions: string | null
  status: string
  created_at: string
  updated_at: string
}

// ===== AI 问诊 =====
export interface DiagnosisRequest {
  age: number
  gender: string
  symptoms: string
  allergies?: string
  medications?: string
}

export interface DiagnosisResult {
  id: string
  ai_output: string
  disclaimer: string
  created_at: string
}

export interface DiagnosisHistoryItem {
  id: string
  input_data: DiagnosisRequest
  ai_output: string
  created_at: string
}

// ===== 搭配建议 =====
export interface PairingRequest {
  herb_ids: string[]
}

export interface PairingResult {
  suggestion: string
  disclaimer: string
  herbs: Array<{
    id: string
    name: string
    unsuitable_groups: string
    precautions: string
  }>
}

// ===== 咨询 =====
export interface ConsultationRequest {
  name: string
  contact: string
  subject: string
  description: string
}

export interface ConsultationResponse {
  id: string
  wechat_id: string
  qr_code_url: string
}

// ===== 商品 =====
export interface Product {
  id: string
  name: string
  category: string | null
  price: number
  specification: string | null
  description: string | null
  image_url: string | null
  stock: number
  status: string
  created_at: string
}

// ===== 购物车 =====
export interface CartItem {
  id: string
  product_id: string
  product_name: string
  product_price: number
  product_image: string
  quantity: number
}

export interface AddCartRequest {
  product_id: string
  quantity: number
}

// ===== 订单 =====
export interface OrderItem {
  product_id: string
  product_name: string
  quantity: number
  unit_price: number
}

export interface Order {
  id: string
  order_no: string
  total_amount: number
  status: string
  items: OrderItem[]
  created_at: string
}

export interface CreateOrderRequest {
  items: Array<{
    product_id: string
    quantity: number
  }>
}
