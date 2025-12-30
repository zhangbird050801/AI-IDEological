import { request } from '@/utils/http'

export function getGenerationHistory(params = {}) {
  return request.get('/aigc/enhanced/history', { params })
}

export function createGenerationHistory(data = {}) {
  return request.post('/aigc/enhanced/history', data)
}

export function rateGenerationHistory(historyId, rating) {
  return request.post(`/aigc/enhanced/history/${historyId}/rate`, null, {
    params: { rating },
  })
}

export function saveHistoryAsCase(historyId) {
  return request.post(`/aigc/enhanced/history/${historyId}/save-as-case`)
}
