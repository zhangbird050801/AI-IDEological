import { defineStore } from 'pinia'
import { shallowRef } from 'vue'
import { basicRoutes, vueModules } from '@/router/routes'
import Layout from '@/layout/index.vue'
import api from '@/api'

// 捕获所有视图组件以便兜底解析（非 index.vue 的单文件）
const allViewModules = import.meta.glob('@/views/**/*.vue')

function resolveViewComponent(componentPath) {
  const indexKey = `/src/views${componentPath}/index.vue`
  const directKey = `/src/views${componentPath}.vue`
  return vueModules[indexKey] || allViewModules[indexKey] || allViewModules[directKey]
}

// * 后端路由相关函数
// 根据后端传来数据构建出前端路由

function normalizeMenuItem(item) {
  const normalized = { ...item }

  // 展示名称调整：课程列表 -> 章节管理
  if (normalized.component === '/courses' && normalized.name === '课程列表') {
    normalized.name = '章节管理'
  }

  if (Array.isArray(normalized.children)) {
    normalized.children = normalized.children.map((child) => normalizeMenuItem(child))
  }

  return normalized
}

function dedupeMenuTree(items = []) {
  const seen = new Set()

  return items.reduce((acc, raw) => {
    const item = normalizeMenuItem(raw)
    const key = `${item.name}|${item.path}|${item.component || ''}`
    if (seen.has(key)) return acc
    seen.add(key)

    const dedupedChildren = Array.isArray(item.children) ? dedupeMenuTree(item.children) : []
    acc.push({ ...item, children: dedupedChildren })
    return acc
  }, [])
}

function buildRoutes(routes = []) {
  return routes.map((e) => {
    const route = {
      name: e.name,
      path: e.path,
      component: shallowRef(Layout),
      isHidden: e.is_hidden,
      redirect: e.redirect,
      meta: {
        title: e.name,
        icon: e.icon,
        order: e.order,
        keepAlive: e.keepalive,
      },
      children: [],
    }

    if (e.children && e.children.length > 0) {
      // 有子菜单
      route.children = e.children.map((e_child) => ({
        name: e_child.name,
        path: e_child.path,
        component: resolveViewComponent(e_child.component),
        isHidden: e_child.is_hidden,
        meta: {
          title: e_child.name,
          icon: e_child.icon,
          order: e_child.order,
          keepAlive: e_child.keepalive,
        },
      }))
    } else {
      // 没有子菜单，创建一个默认的子路由
      route.children.push({
        name: `${e.name}Default`,
        path: '',
        component: resolveViewComponent(e.component),
        isHidden: true,
        meta: {
          title: e.name,
          icon: e.icon,
          order: e.order,
          keepAlive: e.keepalive,
        },
      })
    }

    return route
  })
}

export const usePermissionStore = defineStore('permission', {
  state() {
    return {
      accessRoutes: [],
      accessApis: [],
    }
  },
  getters: {
    routes() {
      return basicRoutes.concat(this.accessRoutes)
    },
    menus() {
      return this.routes.filter((route) => route.name && !route.isHidden)
    },
    apis() {
      return this.accessApis
    },
  },
  actions: {
    async generateRoutes() {
      const res = await api.getUserMenu() // 调用接口获取后端传来的菜单路由
      // Support multiple possible shapes: plain array, { data: [...] }, or envelope { code, data }
      const menuPayload = Array.isArray(res) ? res : res && (res.data ?? res)
      const normalizedMenus = dedupeMenuTree(menuPayload || [])

      this.accessRoutes = buildRoutes(normalizedMenus) // 处理成前端路由格式
      return this.accessRoutes
    },
    async getAccessApis() {
      const res = await api.getUserApi()
      this.accessApis = res?.data ?? res ?? []
      return this.accessApis
    },
    resetPermission() {
      this.$reset()
    },
  },
})
