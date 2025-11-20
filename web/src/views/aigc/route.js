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
      name: 'AIGCChat',
      path: 'chat',
      component: () => import('@/views/aigc/chat/index.vue'),
      meta: {
        title: 'AIGC对话',
        icon: 'mdi:chat-outline',
      },
    },
    {
      name: 'AIGCCases',
      path: 'cases',
      component: () => import('@/views/aigc/cases/index.vue'),
      meta: {
        title: '案例库',
        icon: 'mdi:book-outline',
      },
    },
    {
      name: 'AIGCPrompts',
      path: 'prompts',
      component: () => import('@/views/aigc/prompts/index.vue'),
      meta: {
        title: '提示词模板',
        icon: 'mdi:file-document-outline',
      },
    },
    {
      name: 'AIGCResources',
      path: 'resources',
      component: () => import('@/views/aigc/resources/index.vue'),
      meta: {
        title: '教学资源',
        icon: 'mdi:folder-outline',
      },
    },
  ],
}