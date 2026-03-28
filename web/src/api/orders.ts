import client from './client'
import type { CreateOrderRequest, Order, PaginatedData } from '../types'

export function createOrder(data: CreateOrderRequest): Promise<Order> {
  return client.post('/api/v1/orders', data)
}

export function getOrderList(page?: number): Promise<PaginatedData<Order>> {
  return client.get('/api/v1/orders', { params: { page } })
}
