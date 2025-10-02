import axios from 'axios'
import { resReject, resResolve, reqReject, reqResolve } from './interceptors'

export function createAxios(options = {}) {
  // Prefer a Vite-provided timeout for AIGC requests, fallback to 60000ms (60s)
  const envTimeout = Number(import.meta.env.VITE_AIGC_TIMEOUT || import.meta.env.VITE_TIMEOUT || 0)
  const defaultOptions = {
    timeout: envTimeout > 0 ? envTimeout : 60000,
  }
  const service = axios.create({
    ...defaultOptions,
    ...options,
  })
  service.interceptors.request.use(reqResolve, reqReject)
  service.interceptors.response.use(resResolve, resReject)
  return service
}

export const request = createAxios({
  baseURL: import.meta.env.VITE_BASE_API,
})
