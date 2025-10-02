import { request } from '@/utils/http'

// Accepts either:
// - an array of messages: [{ role, content }, ...]
// - a single string (user content) -> convert to messages array
export function chatAPI(messages) {
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

  return request.post('/aigc/chat', { messages: payloadMessages })
}

// Streamed chat via Server-Sent Events (SSE)
export function chatStream(messages) {
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

  const controller = new AbortController()

  // Return an async iterator for the caller to consume chunks
  async function* streamGenerator() {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: payloadMessages }),
      signal: controller.signal,
    })

    if (!resp.ok) {
      const text = await resp.text()
      throw new Error(`Stream request failed: ${resp.status} ${text}`)
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buf = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      // SSE lines end with \n\n; process available lines
      let idx
      while ((idx = buf.indexOf('\n\n')) !== -1) {
        const chunk = buf.slice(0, idx)
        buf = buf.slice(idx + 2)
        // Each chunk may contain multiple lines; extract data: prefixes
        for (const line of chunk.split(/\r?\n/)) {
          const trimmed = line.trim()
          if (!trimmed) continue
          if (trimmed.startsWith('data:')) {
            const payload = trimmed.slice('data:'.length).trim()
            if (payload === '[DONE]') return
            // try parse JSON, otherwise return text wrapper
            try {
              const obj = JSON.parse(payload)
              yield { type: 'chunk', payload: obj }
            } catch (e) {
              yield { type: 'text', payload }
            }
          } else if (trimmed.startsWith('event:')) {
            // ignore for now
            continue
          } else {
            yield { type: 'text', payload: trimmed }
          }
        }
      }
    }

    // process any trailing buffer
    if (buf.trim()) {
      for (const line of buf.split(/\r?\n/)) {
        const trimmed = line.trim()
        if (!trimmed) continue
        if (trimmed.startsWith('data:')) {
          const payload = trimmed.slice('data:'.length).trim()
          if (payload !== '[DONE]') {
            try {
              const obj = JSON.parse(payload)
              yield { type: 'chunk', payload: obj }
            } catch (e) {
              yield { type: 'text', payload }
            }
          }
        } else yield trimmed
      }
    }
  }

  const iterator = streamGenerator()
  iterator.cancel = () => controller.abort()
  return iterator
}
