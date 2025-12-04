const Layout = () => import('@/layout/index.vue')

// 课程管理菜单已移除，相关功能已整合到"课程思政"菜单中
// 如需访问课程管理功能，请前往"课程思政"菜单下的"章节管理"和"案例分类"

export default {
  name: '课程管理',
  path: '/courses',
  component: Layout,
  redirect: '/aigc/chapters', // 重定向到新位置
  meta: {
    title: '课程管理',
    icon: 'material-symbols:school-outline',
    order: 999, // 设置很大的order值，使其排在最后
    hidden: true, // 隐藏此菜单
  },
  children: [
    // 保留路由以兼容旧链接，但隐藏在菜单中
    {
      name: '课程列表',
      path: 'index',
      component: () => import('./index.vue'),
      meta: {
        title: '章节管理',
        icon: 'material-symbols:list',
        hidden: true,
      },
    },
    {
      name: '章节管理旧',
      path: 'chapters/:courseId',
      component: () => import('./chapters.vue'),
      meta: {
        title: '章节管理',
        icon: 'material-symbols:menu-book',
        hidden: true,
      },
    },
    {
      name: '知识点管理旧',
      path: 'knowledge-points/:courseId',
      component: () => import('./knowledge-points.vue'),
      meta: {
        title: '知识点管理',
        icon: 'material-symbols:lightbulb-outline',
        hidden: true,
      },
    },
    {
      name: '案例分类旧',
      path: 'categories',
      component: () => import('./categories.vue'),
      meta: {
        title: '案例分类',
        icon: 'material-symbols:category-outline',
        hidden: true,
      },
    },
  ],
}
