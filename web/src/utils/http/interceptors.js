import { getToken } from '@/utils'
import { resolveResError } from './helpers'
import { useUserStore } from '@/store'

export function reqResolve(config) {
  // 处理不需要token的请求
  if (config.noNeedToken) {
    return config
  }

  const token = getToken()
  if (token) {
    config.headers.token = config.headers.token || token
  }

  return config
}

export function reqReject(error) {
  return Promise.reject(error)
}

export function resResolve(response) {
  const { data, status, statusText } = response
  // If the backend uses the { code, msg, data } envelope, honor it.
  // If no `code` field exists, treat the response as successful and return the body.
  if (data && Object.prototype.hasOwnProperty.call(data, 'code')) {
    if (data.code !== 200) {
      const code = data.code ?? status
      const message = resolveResError(code, data?.msg ?? statusText)
      window.$message?.error(message, { keepAliveOnHover: true })
      return Promise.reject({ code, message, error: data || response })
    }
    // Envelope present and code == 200: keep original envelope so callers can still use res.data
    return Promise.resolve(data)
  }

  // No `code` field: wrap plain body into an object with `data` to preserve previous caller expectations
  return Promise.resolve({ data })
}

export async function resReject(error) {
  if (!error || !error.response) {
    const code = error?.code
    /** 根据code处理对应的操作，并返回处理后的message */
    const message = resolveResError(code, error.message)
    window.$message?.error(message)
    return Promise.reject({ code, message, error })
  }
  const { data, status } = error.response

  if (data?.code === 401) {
    try {
      const userStore = useUserStore()
      userStore.logout()
    } catch (error) {
      // 记录拦截器错误，方便调试
      return
    }
  }
  // 后端返回的response数据
  const code = data?.code ?? status
  const message = resolveResError(code, data?.msg ?? error.message)
  window.$message?.error(message, { keepAliveOnHover: true })
  return Promise.reject({ code, message, error: error.response?.data || error.response })
}
