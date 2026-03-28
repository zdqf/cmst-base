import client from './client'
import type { PaginatedData, HerbListItem, HerbDetail } from '../types'

export function getHerbList(params?: {
  page?: number
  page_size?: number
  category?: string
  keyword?: string
}): Promise<PaginatedData<HerbListItem>> {
  return client.get('/api/v1/herbs', { params })
}

export function getHerbDetail(id: string): Promise<HerbDetail> {
  return client.get(`/api/v1/herbs/${id}`)
}

export function getDailyHerb(): Promise<HerbDetail> {
  return client.get('/api/v1/herbs/daily')
}
