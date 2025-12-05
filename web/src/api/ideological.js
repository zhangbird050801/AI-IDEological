import { request } from '@/utils'

// 案例库相关API
export const casesApi = {
  // 获取案例列表
  getList: (params = {}) => request.get('/ideological/cases/', { params }),
  // 创建案例
  create: (data = {}) => request.post('/ideological/cases/', data),
  // 获取案例详情
  getById: (id) => request.get(`/ideological/cases/${id}`),
  // 更新案例
  update: (id, data = {}) => request.put(`/ideological/cases/${id}`, data),
  // 删除案例
  delete: (id) => request.delete(`/ideological/cases/${id}`),
  // 批量操作
  batchOperation: (data = {}) => request.post('/ideological/cases/batch', data),
  // 获取热门案例
  getHot: (params = {}) => request.get('/ideological/cases/hot/list', { params }),
  // 获取推荐案例
  getRecommended: (params = {}) => request.get('/ideological/cases/recommended/list', { params }),
  // 评分案例
  rate: (id, rating) => request.post(`/ideological/cases/${id}/rate`, {}, { params: { rating } }),
  // 获取章节列表
  getChapters: () => request.get('/ideological/cases/chapters/list'),
  // 获取思政主题列表
  getThemes: () => request.get('/ideological/cases/themes/list'),
}

// 提示词模板相关API
export const templatesApi = {
  // 获取模板列表
  getList: (params = {}) => request.get('/ideological/templates/', { params }),
  // 创建模板
  create: (data = {}) => request.post('/ideological/templates/', data),
  // 获取模板详情
  getById: (id) => request.get(`/ideological/templates/${id}`),
  // 更新模板
  update: (id, data = {}) => request.put(`/ideological/templates/${id}`, data),
  // 删除模板
  delete: (id) => request.delete(`/ideological/templates/${id}`),
  // 批量操作
  batchOperation: (data = {}) => request.post('/ideological/templates/batch', data),
  // 获取系统模板
  getSystem: () => request.get('/ideological/templates/system/list'),
  // 评分模板
  rate: (id, rating) => request.post(`/ideological/templates/${id}/rate`, {}, { params: { rating } }),
  // 渲染模板
  render: (id, variables) => request.post(`/ideological/templates/${id}/render`, variables),
  // 获取模板类型列表
  getTypes: () => request.get('/ideological/templates/types/list'),
  // 获取模板分类列表
  getCategories: () => request.get('/ideological/templates/categories/list'),
  // 获取思政主题列表
  getThemes: () => request.get('/ideological/templates/themes/list'),
}

// 教学资源相关API
export const resourcesApi = {
  // 获取资源列表
  getList: (params = {}) => request.get('/ideological/resources/', { params }),
  // 创建资源
  create: (data = {}) => {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (data[key] !== undefined && data[key] !== null) {
        formData.append(key, data[key])
      }
    })
    return request.post('/ideological/resources/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  // 获取资源详情
  getById: (id) => request.get(`/ideological/resources/${id}`),
  // 更新资源
  update: (id, data = {}) => request.put(`/ideological/resources/${id}`, data),
  // 删除资源
  delete: (id) => request.delete(`/ideological/resources/${id}`),
  // 批量操作
  batchOperation: (data = {}) => request.post('/ideological/resources/batch', data),
  // 获取热门资源
  getHot: (params = {}) => request.get('/ideological/resources/hot/list', { params }),
  // 下载文件
  download: (fileUuid) => request.get(`/ideological/resources/download/${fileUuid}`, { responseType: 'blob' }),
  // 获取资源类型列表
  getTypes: () => request.get('/ideological/resources/types/list'),
  // 获取思政主题列表
  getThemes: () => request.get('/ideological/resources/themes/list'),
}

// 思政主题分类相关API
export const themeCategoriesApi = {
  // 获取分类树
  getTree: () => request.get('/ideological/theme-categories/tree'),
  // 获取分类列表（扁平）
  getList: () => request.get('/ideological/theme-categories/list'),
  // 获取主题名称列表（用于选择器）
  getNames: () => request.get('/ideological/theme-categories/names', { params: { _t: Date.now() } }),
  // 获取分类详情
  getById: (id) => request.get(`/ideological/theme-categories/${id}`),
  // 创建分类
  create: (data = {}) => request.post('/ideological/theme-categories', data),
  // 更新分类
  update: (id, data = {}) => request.put(`/ideological/theme-categories/${id}`, data),
  // 删除分类
  delete: (id) => request.delete(`/ideological/theme-categories/${id}`),
  // 移动分类（拖拽）
  move: (id, data = {}) => request.post(`/ideological/theme-categories/${id}/move`, {}, { params: data }),
}