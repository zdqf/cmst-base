import client from './client'
import type { ConsultationRequest, ConsultationResponse } from '../types'

export function submitConsultation(
  data: ConsultationRequest,
): Promise<ConsultationResponse> {
  return client.post('/api/v1/consultations', data)
}
