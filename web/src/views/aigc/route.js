export default {
  name: 'AIGC',
  path: '/aigc',
  component: () => import('@/layout/index.vue'),
  redirect: '/aigc/chat',
  meta: {
    title: '课程思政',
    icon: 'mdi:school-outline',
    order: 2,
  },
  children: [
    {
      name: '章节管理',
      path: 'index',
      component: () => import('@/views/courses/index.vue'),
      meta: {
        title: '章节管理',
        icon: 'material-symbols:menu-book',
        order: 1,
      },
    },
    {
      name: 'ThemeCategories',
      path: 'theme-categories',
      component: () => import('@/views/aigc/theme-categories/index.vue'),
      meta: {
        title: '思政主题分类',
        icon: 'material-symbols:category-outline',
        order: 2,
      },
    },
    {
      name: 'AIGCChat',
      path: 'chat',
      component: () => import('@/views/aigc/chat/index.vue'),
      meta: {
        title: 'AIGC对话',
        icon: 'mdi:chat-outline',
        order: 3,
      },
    },
    {
      name: 'AIGCCases',
      path: 'cases',
      component: () => import('@/views/aigc/cases/index.vue'),
      meta: {
        title: '案例库',
        icon: 'mdi:book-outline',
        order: 4,
      },
    },
    {
      name: 'AIGCPrompts',
      path: 'prompts',
      component: () => import('@/views/aigc/prompts/index.vue'),
      meta: {
        title: '提示词模板',
        icon: 'mdi:file-document-outline',
        order: 5,
      },
    },
    {
      name: 'AIGCPromptAssistant',
      path: 'prompt-assistant',
      component: () => import('@/views/aigc/prompt-assistant/index.vue'),
      meta: {
        title: '提示词助手',
        icon: 'mdi:robot-outline',
        keepAlive: false, // 禁用缓存以确保页面刷新
        order: 6,
      },
    },
    {
      name: 'AIGCResources',
      path: 'resources',
      component: () => import('@/views/aigc/resources/index.vue'),
      meta: {
        title: '教学资源',
        icon: 'mdi:folder-outline',
        order: 7,
      },
    },
    {
      name: 'AIGCHistory',
      path: 'history',
      component: () => import('@/views/aigc/history/index.vue'),
      meta: {
        title: '生成历史',
        icon: 'mdi:history',
        order: 8,
      },
    },
  ],
}
