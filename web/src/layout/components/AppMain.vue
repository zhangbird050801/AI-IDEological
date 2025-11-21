<template>
  <router-view v-slot="{ Component, route }">
    <KeepAlive :include="keepAliveRouteNames" :max="10">
      <component
        :is="Component"
        v-if="appStore.reloadFlag"
        :key="getRouteKey(route)"
      />
    </KeepAlive>
  </router-view>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useAppStore } from '@/store'
import { useRouter } from 'vue-router'
const appStore = useAppStore()
const router = useRouter()

// 动态获取路由，避免缓存问题
const keepAliveRouteNames = computed(() => {
  const allRoutes = router.getRoutes()
  return allRoutes
    .filter((route) => route.meta?.keepAlive && route.name)
    .map((route) => route.name)
})

// 生成路由key，确保组件正确重新渲染
const getRouteKey = (route) => {
  // 对于需要强制刷新的路由，使用时间戳
  if (route.meta?.keepAlive === false) {
    return `${route.name}-${Date.now()}`
  }
  return appStore.aliveKeys[route.name] || route.fullPath
}
</script>
