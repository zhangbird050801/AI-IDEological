import { request } from '@/utils/http'

// Accepts either:
// - an array of messages: [{ role, content }, ...]
// - a single string (user content) -> convert to messages array
export function chatAPI(messages, options = {}) {
  let payloadMessages = messages
  // if caller passed a plain string, wrap into a user message
  if (typeof messages === 'string') {
    payloadMessages = [{ role: 'user', content: messages }]
  }

  // if caller passed a single message object (not an array), normalize it
  if (messages && !Array.isArray(messages) && typeof messages === 'object') {
    const m = messages
    if (m.role && m.content) payloadMessages = [m]
    else payloadMessages = [{ role: 'user', content: String(m) }]
  }

  return request.post('/aigc/chat', { 
    messages: payloadMessages,
    enable_web_search: options.enableWebSearch || false
  })
}

// Streamed chat via Server-Sent Events (SSE)
export function chatStream(messages, options = {}) {
  let payloadMessages = messages
  if (typeof messages === 'string') {
    payloadMessages = [{ role: 'user', content: messages }]
  }
  if (messages && !Array.isArray(messages) && typeof messages === 'object') {
    const m = messages
    if (m.role && m.content) payloadMessages = [m]
    else payloadMessages = [{ role: 'user', content: String(m) }]
  }

  const base = import.meta.env.VITE_BASE_API || ''
  const url = `${base}/aigc/chat/stream`
  
  const payload = { 
    messages: payloadMessages,
    enable_web_search: options.enableWebSearch || false
  }

  const controller = new AbortController()

  // Return an async iterator for the caller to consume chunks
  async function* streamGenerator() {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })

    if (!resp.ok) {
      const text = await resp.text()
      throw new Error(`Stream request failed: ${resp.status} ${text}`)
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')

      // 保留最后一行（可能不完整）
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line) continue
        if (line.startsWith('data:')) {
          // Preserve whitespace/newlines in content: do NOT trim payload.
          const payload = line.slice('data:'.length).replace(/^\s+/, '').replace(/\r$/, '')
          if (payload === '[DONE]') return
          try {
            const obj = JSON.parse(payload)
            yield { type: 'chunk', payload: obj }
          } catch (e) {
            yield { type: 'text', payload }
          }
        }
      }
    }
  }

  const iterator = streamGenerator()
  iterator.cancel = () => controller.abort()
  return iterator
}
