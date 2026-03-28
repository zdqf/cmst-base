import client from './client'
import type { PaginatedData, Product } from '../types'

export function getProductList(params?: {
  page?: number
  page_size?: number
  category?: string
}): Promise<PaginatedData<Product>> {
  return client.get('/api/v1/products', { params })
}

export function getProductDetail(id: string): Promise<Product> {
  return client.get(`/api/v1/products/${id}`)
}
