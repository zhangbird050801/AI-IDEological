// 开发环境快速认证工具
import { setToken } from './auth/token'

export function setupDevAuth() {
  // 检查是否是开发环境
  if (import.meta.env.DEV) {
    // 检查是否已经有token
    const currentToken = localStorage.getItem('access_token')
    if (!currentToken) {
      // 设置开发环境的默认token
      setToken('dev')
      // 开发环境：设置默认认证token
    }
  }
}

export function ensureDevAuth() {
  if (import.meta.env.DEV) {
    const currentToken = localStorage.getItem('access_token')
    if (!currentToken || currentToken !== 'dev') {
      setToken('dev')
      // 开发环境：重置认证token
    }
  }
}
