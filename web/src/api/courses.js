import { request } from '@/utils'

/**
 * Course Management API Client
 * Provides methods for course, chapter, knowledge point, and category operations
 */

// ==================== Course APIs ====================

/**
 * Get paginated course list
 * @param {Object} params - Query parameters
 * @param {number} params.page - Page number (default: 1)
 * @param {number} params.size - Page size (default: 10)
 * @param {string} params.keyword - Search keyword
 * @param {boolean} params.is_active - Filter by active status
 * @returns {Promise<{items: Array, total: number, page: number, size: number}>}
 */
export function getCourses(params = {}) {
  return request.get('/courses/', { params })
}

/**
 * Get all courses without pagination
 * @param {boolean} is_active - Filter by active status (default: true)
 * @returns {Promise<Array>}
 */
export function getAllCourses(is_active = true) {
  return request.get('/courses/all', { params: { is_active } })
}

/**
 * Get course by ID
 * @param {number} id - Course ID
 * @returns {Promise<Object>}
 */
export function getCourse(id) {
  return request.get(`/courses/${id}`)
}

/**
 * Create new course
 * @param {Object} data - Course data
 * @param {string} data.name - Course name (required)
 * @param {string} data.code - Course code (required)
 * @param {string} data.description - Course description
 * @param {number} data.credit_hours - Credit hours
 * @returns {Promise<Object>}
 */
export function createCourse(data) {
  return request.post('/courses/', data)
}

/**
 * Update course
 * @param {number} id - Course ID
 * @param {Object} data - Course data to update
 * @returns {Promise<Object>}
 */
export function updateCourse(id, data) {
  return request.put(`/courses/${id}`, data)
}

/**
 * Delete course
 * @param {number} id - Course ID
 * @returns {Promise<Object>}
 */
export function deleteCourse(id) {
  return request.delete(`/courses/${id}`)
}

// ==================== Chapter APIs ====================

/**
 * Get chapters by course ID
 * @param {number} courseId - Course ID
 * @returns {Promise<Array>}
 */
export function getChaptersByCourse(courseId) {
  return request.get('/chapters/', { params: { course_id: courseId } })
}

/**
 * Get chapter by ID
 * @param {number} id - Chapter ID
 * @returns {Promise<Object>}
 */
export function getChapter(id) {
  return request.get(`/chapters/${id}`)
}

/**
 * Create new chapter
 * @param {Object} data - Chapter data
 * @param {number} data.course_id - Course ID (required)
 * @param {string} data.name - Chapter name (required)
 * @param {string} data.description - Chapter description
 * @param {number} data.order_num - Order number
 * @returns {Promise<Object>}
 */
export function createChapter(data) {
  return request.post('/chapters/', data)
}

/**
 * Update chapter
 * @param {number} id - Chapter ID
 * @param {Object} data - Chapter data to update
 * @returns {Promise<Object>}
 */
export function updateChapter(id, data) {
  return request.put(`/chapters/${id}`, data)
}

/**
 * Delete chapter
 * @param {number} id - Chapter ID
 * @returns {Promise<Object>}
 */
export function deleteChapter(id) {
  return request.delete(`/chapters/${id}`)
}

/**
 * Reorder chapters
 * @param {Array<{id: number, order_num: number}>} chapters - Array of chapter IDs and new order numbers
 * @returns {Promise<Object>}
 */
export function reorderChapters(chapters) {
  return request.post('/chapters/reorder', { chapters })
}

// ==================== Knowledge Point APIs ====================

/**
 * Get knowledge points by chapter ID
 * @param {number} chapterId - Chapter ID
 * @returns {Promise<Array>}
 */
export function getKnowledgePointsByChapter(chapterId) {
  return request.get('/knowledge-points/', { params: { chapter_id: chapterId } })
}

/**
 * Get knowledge point by ID
 * @param {number} id - Knowledge point ID
 * @returns {Promise<Object>}
 */
export function getKnowledgePoint(id) {
  return request.get(`/knowledge-points/${id}`)
}

/**
 * Create new knowledge point
 * @param {Object} data - Knowledge point data
 * @param {number} data.chapter_id - Chapter ID (required)
 * @param {string} data.name - Knowledge point name (required)
 * @param {string} data.description - Description
 * @param {Array<string>} data.keywords - Keywords array
 * @returns {Promise<Object>}
 */
export function createKnowledgePoint(data) {
  return request.post('/knowledge-points/', data)
}

/**
 * Update knowledge point
 * @param {number} id - Knowledge point ID
 * @param {Object} data - Knowledge point data to update
 * @returns {Promise<Object>}
 */
export function updateKnowledgePoint(id, data) {
  return request.put(`/knowledge-points/${id}`, data)
}

/**
 * Delete knowledge point
 * @param {number} id - Knowledge point ID
 * @returns {Promise<Object>}
 */
export function deleteKnowledgePoint(id) {
  return request.delete(`/knowledge-points/${id}`)
}

/**
 * Reorder knowledge points
 * @param {Array<{id: number, order: number}>} knowledgePoints - Array of knowledge point IDs and new order numbers
 * @returns {Promise<Object>}
 */
export function reorderKnowledgePoints(knowledgePoints) {
  return request.post('/knowledge-points/reorder', { knowledge_points: knowledgePoints })
}

// ==================== Case Category APIs ====================

/**
 * Get all categories in tree structure
 * @returns {Promise<Array>}
 */
export function getCategoryTree() {
  return request.get('/case-categories/tree')
}

/**
 * Get category by ID
 * @param {number} id - Category ID
 * @returns {Promise<Object>}
 */
export function getCategory(id) {
  return request.get(`/case-categories/${id}`)
}

/**
 * Create new category
 * @param {Object} data - Category data
 * @param {string} data.name - Category name (required)
 * @param {string} data.description - Description
 * @param {number} data.parent_id - Parent category ID
 * @returns {Promise<Object>}
 */
export function createCategory(data) {
  return request.post('/case-categories/', data)
}

/**
 * Update category
 * @param {number} id - Category ID
 * @param {Object} data - Category data to update
 * @returns {Promise<Object>}
 */
export function updateCategory(id, data) {
  return request.put(`/case-categories/${id}`, data)
}

/**
 * Delete category
 * @param {number} id - Category ID
 * @returns {Promise<Object>}
 */
export function deleteCategory(id) {
  return request.delete(`/case-categories/${id}`)
}

/**
 * Move category to new parent (drag and drop)
 * @param {number} id - Category ID to move
 * @param {Object} data - Move data
 * @param {number} data.parent_id - New parent ID
 * @param {number} data.order_num - New order number
 * @returns {Promise<Object>}
 */
export function moveCategory(id, data) {
  return request.post(`/case-categories/${id}/move`, data)
}

export default {
  // Course
  getCourses,
  getAllCourses,
  getCourse,
  createCourse,
  updateCourse,
  deleteCourse,
  // Chapter
  getChaptersByCourse,
  getChapter,
  createChapter,
  updateChapter,
  deleteChapter,
  reorderChapters,
  // Knowledge Point
  getKnowledgePointsByChapter,
  getKnowledgePoint,
  createKnowledgePoint,
  updateKnowledgePoint,
  deleteKnowledgePoint,
  reorderKnowledgePoints,
  // Category
  getCategoryTree,
  getCategory,
  createCategory,
  updateCategory,
  deleteCategory,
  moveCategory,
}
