import client from './client'
import type {
  DiagnosisRequest,
  DiagnosisResult,
  DiagnosisHistoryItem,
  PaginatedData,
  PairingResult,
} from '../types'

export function submitDiagnosis(data: DiagnosisRequest): Promise<DiagnosisResult> {
  return client.post('/api/v1/ai/diagnosis', data)
}

export function getDiagnosisHistory(
  page?: number,
): Promise<PaginatedData<DiagnosisHistoryItem>> {
  return client.get('/api/v1/ai/diagnosis/history', { params: { page } })
}

export function submitPairing(herbIds: string[]): Promise<PairingResult> {
  return client.post('/api/v1/ai/pairing', { herb_ids: herbIds })
}
