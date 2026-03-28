import client from './client'
import type { CartItem, AddCartRequest } from '../types'

export function getCart(): Promise<CartItem[]> {
  return client.get('/api/v1/cart')
}

export function addToCart(data: AddCartRequest): Promise<void> {
  return client.post('/api/v1/cart', data)
}

export function updateCartItem(id: string, quantity: number): Promise<void> {
  return client.put(`/api/v1/cart/${id}`, { quantity })
}

export function removeCartItem(id: string): Promise<void> {
  return client.delete(`/api/v1/cart/${id}`)
}
