/** 重置样式 */
import '@/styles/reset.css'
import 'uno.css'
import '@/styles/global.scss'

import { createApp } from 'vue'
import { setupRouter } from '@/router'
import { setupStore } from '@/store'
import App from './App.vue'
import { setupDirectives } from './directives'
import { useResize } from '@/utils'
import i18n from '~/i18n'
import { setupDevAuth } from '@/utils/dev-auth'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 配置naive-ui的代码高亮
window.hljs = hljs

async function setupApp() {
  // 开发环境认证设置
  setupDevAuth()

  const app = createApp(App)

  setupStore(app)

  await setupRouter(app)
  setupDirectives(app)
  app.use(useResize)
  app.use(i18n)
  app.mount('#app')
}

setupApp()
