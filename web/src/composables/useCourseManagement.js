import { ref, computed } from 'vue'
import * as courseApi from '@/api/courses'

/**
 * Composable for course management shared state and logic
 * Provides reactive state and methods for managing courses, chapters, knowledge points, and categories
 */
export function useCourseManagement() {
  // ==================== State ====================
  
  // Course state
  const courses = ref([])
  const currentCourse = ref(null)
  const coursesLoading = ref(false)
  const coursesTotal = ref(0)
  
  // Chapter state
  const chapters = ref([])
  const currentChapter = ref(null)
  const chaptersLoading = ref(false)
  
  // Knowledge point state
  const knowledgePoints = ref([])
  const currentKnowledgePoint = ref(null)
  const knowledgePointsLoading = ref(false)
  
  // Category state
  const categoryTree = ref([])
  const categoriesLoading = ref(false)
  
  // Error state
  const error = ref(null)
  
  // ==================== Computed ====================
  
  /**
   * Get active courses only
   */
  const activeCourses = computed(() => {
    return courses.value.filter(course => course.is_active)
  })
  
  /**
   * Get chapters for current course
   */
  const currentCourseChapters = computed(() => {
    if (!currentCourse.value) return []
    return chapters.value.filter(chapter => chapter.course_id === currentCourse.value.id)
  })
  
  /**
   * Get knowledge points for current chapter
   */
  const currentChapterKnowledgePoints = computed(() => {
    if (!currentChapter.value) return []
    return knowledgePoints.value.filter(kp => kp.chapter_id === currentChapter.value.id)
  })
  
  // ==================== Course Methods ====================
  
  /**
   * Fetch courses with pagination
   * @param {Object} params - Query parameters
   */
  async function fetchCourses(params = {}) {
    try {
      coursesLoading.value = true
      error.value = null
      const response = await courseApi.getCourses(params)
      
      // Handle both envelope formats: { data: { items, total } } and { items, total }
      const data = response.data || response
      courses.value = data.items || []
      coursesTotal.value = data.total || 0
      
      return data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      coursesLoading.value = false
    }
  }
  
  /**
   * Fetch all courses without pagination
   * @param {boolean} isActive - Filter by active status
   */
  async function fetchAllCourses(isActive = true) {
    try {
      coursesLoading.value = true
      error.value = null
      const response = await courseApi.getAllCourses(isActive)
      
      // Handle envelope format
      courses.value = response.data || response
      
      return courses.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      coursesLoading.value = false
    }
  }
  
  /**
   * Fetch single course by ID
   * @param {number} id - Course ID
   */
  async function fetchCourse(id) {
    try {
      coursesLoading.value = true
      error.value = null
      const response = await courseApi.getCourse(id)
      
      currentCourse.value = response.data || response
      return currentCourse.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      coursesLoading.value = false
    }
  }
  
  /**
   * Create new course
   * @param {Object} courseData - Course data
   */
  async function createCourse(courseData) {
    try {
      error.value = null
      const response = await courseApi.createCourse(courseData)
      const newCourse = response.data || response
      
      // Add to local state
      courses.value.push(newCourse)
      coursesTotal.value += 1
      
      return newCourse
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Update existing course
   * @param {number} id - Course ID
   * @param {Object} courseData - Course data to update
   */
  async function updateCourse(id, courseData) {
    try {
      error.value = null
      const response = await courseApi.updateCourse(id, courseData)
      const updatedCourse = response.data || response
      
      // Update in local state
      const index = courses.value.findIndex(c => c.id === id)
      if (index !== -1) {
        courses.value[index] = updatedCourse
      }
      
      // Update current course if it's the one being edited
      if (currentCourse.value?.id === id) {
        currentCourse.value = updatedCourse
      }
      
      return updatedCourse
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Delete course
   * @param {number} id - Course ID
   */
  async function deleteCourse(id) {
    try {
      error.value = null
      await courseApi.deleteCourse(id)
      
      // Remove from local state
      courses.value = courses.value.filter(c => c.id !== id)
      coursesTotal.value -= 1
      
      // Clear current course if it was deleted
      if (currentCourse.value?.id === id) {
        currentCourse.value = null
      }
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Set current course
   * @param {Object} course - Course object
   */
  function setCurrentCourse(course) {
    currentCourse.value = course
  }
  
  // ==================== Chapter Methods ====================
  
  /**
   * Fetch chapters by course ID
   * @param {number} courseId - Course ID
   */
  async function fetchChaptersByCourse(courseId) {
    try {
      chaptersLoading.value = true
      error.value = null
      const response = await courseApi.getChaptersByCourse(courseId)
      
      chapters.value = response.data || response
      return chapters.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      chaptersLoading.value = false
    }
  }
  
  /**
   * Create new chapter
   * @param {Object} chapterData - Chapter data
   */
  async function createChapter(chapterData) {
    try {
      error.value = null
      const response = await courseApi.createChapter(chapterData)
      const newChapter = response.data || response
      
      chapters.value.push(newChapter)
      return newChapter
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Update chapter
   * @param {number} id - Chapter ID
   * @param {Object} chapterData - Chapter data to update
   */
  async function updateChapter(id, chapterData) {
    try {
      error.value = null
      const response = await courseApi.updateChapter(id, chapterData)
      const updatedChapter = response.data || response
      
      const index = chapters.value.findIndex(c => c.id === id)
      if (index !== -1) {
        chapters.value[index] = updatedChapter
      }
      
      if (currentChapter.value?.id === id) {
        currentChapter.value = updatedChapter
      }
      
      return updatedChapter
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Delete chapter
   * @param {number} id - Chapter ID
   */
  async function deleteChapter(id) {
    try {
      error.value = null
      await courseApi.deleteChapter(id)
      
      chapters.value = chapters.value.filter(c => c.id !== id)
      
      if (currentChapter.value?.id === id) {
        currentChapter.value = null
      }
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Reorder chapters
   * @param {Array} chaptersOrder - Array of {id, order_num}
   */
  async function reorderChapters(chaptersOrder) {
    try {
      error.value = null
      await courseApi.reorderChapters(chaptersOrder)
      
      // Update local state
      chaptersOrder.forEach(({ id, order_num }) => {
        const chapter = chapters.value.find(c => c.id === id)
        if (chapter) {
          chapter.order_num = order_num
        }
      })
      
      // Sort chapters by order_num
      chapters.value.sort((a, b) => a.order_num - b.order_num)
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Set current chapter
   * @param {Object} chapter - Chapter object
   */
  function setCurrentChapter(chapter) {
    currentChapter.value = chapter
  }
  
  // ==================== Knowledge Point Methods ====================
  
  /**
   * Fetch knowledge points by chapter ID
   * @param {number} chapterId - Chapter ID
   */
  async function fetchKnowledgePointsByChapter(chapterId) {
    try {
      knowledgePointsLoading.value = true
      error.value = null
      const response = await courseApi.getKnowledgePointsByChapter(chapterId)
      
      knowledgePoints.value = response.data || response
      return knowledgePoints.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      knowledgePointsLoading.value = false
    }
  }
  
  /**
   * Create new knowledge point
   * @param {Object} kpData - Knowledge point data
   */
  async function createKnowledgePoint(kpData) {
    try {
      error.value = null
      const response = await courseApi.createKnowledgePoint(kpData)
      const newKP = response.data || response
      
      knowledgePoints.value.push(newKP)
      return newKP
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Update knowledge point
   * @param {number} id - Knowledge point ID
   * @param {Object} kpData - Knowledge point data to update
   */
  async function updateKnowledgePoint(id, kpData) {
    try {
      error.value = null
      const response = await courseApi.updateKnowledgePoint(id, kpData)
      const updatedKP = response.data || response
      
      const index = knowledgePoints.value.findIndex(kp => kp.id === id)
      if (index !== -1) {
        knowledgePoints.value[index] = updatedKP
      }
      
      if (currentKnowledgePoint.value?.id === id) {
        currentKnowledgePoint.value = updatedKP
      }
      
      return updatedKP
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Delete knowledge point
   * @param {number} id - Knowledge point ID
   */
  async function deleteKnowledgePoint(id) {
    try {
      error.value = null
      await courseApi.deleteKnowledgePoint(id)
      
      knowledgePoints.value = knowledgePoints.value.filter(kp => kp.id !== id)
      
      if (currentKnowledgePoint.value?.id === id) {
        currentKnowledgePoint.value = null
      }
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Set current knowledge point
   * @param {Object} kp - Knowledge point object
   */
  function setCurrentKnowledgePoint(kp) {
    currentKnowledgePoint.value = kp
  }
  
  // ==================== Category Methods ====================
  
  /**
   * Fetch category tree
   */
  async function fetchCategoryTree() {
    try {
      categoriesLoading.value = true
      error.value = null
      const response = await courseApi.getCategoryTree()
      
      categoryTree.value = response.data || response
      return categoryTree.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      categoriesLoading.value = false
    }
  }
  
  /**
   * Create new category
   * @param {Object} categoryData - Category data
   */
  async function createCategory(categoryData) {
    try {
      error.value = null
      const response = await courseApi.createCategory(categoryData)
      const newCategory = response.data || response
      
      // Refresh tree to get updated structure
      await fetchCategoryTree()
      
      return newCategory
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Update category
   * @param {number} id - Category ID
   * @param {Object} categoryData - Category data to update
   */
  async function updateCategory(id, categoryData) {
    try {
      error.value = null
      const response = await courseApi.updateCategory(id, categoryData)
      const updatedCategory = response.data || response
      
      // Refresh tree to get updated structure
      await fetchCategoryTree()
      
      return updatedCategory
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Delete category
   * @param {number} id - Category ID
   */
  async function deleteCategory(id) {
    try {
      error.value = null
      await courseApi.deleteCategory(id)
      
      // Refresh tree to get updated structure
      await fetchCategoryTree()
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  /**
   * Move category (drag and drop)
   * @param {number} id - Category ID
   * @param {Object} moveData - Move data {parent_id, order_num}
   */
  async function moveCategory(id, moveData) {
    try {
      error.value = null
      await courseApi.moveCategory(id, moveData)
      
      // Refresh tree to get updated structure
      await fetchCategoryTree()
    } catch (err) {
      error.value = err
      throw err
    }
  }
  
  // ==================== Utility Methods ====================
  
  /**
   * Clear all state
   */
  function clearState() {
    courses.value = []
    currentCourse.value = null
    chapters.value = []
    currentChapter.value = null
    knowledgePoints.value = []
    currentKnowledgePoint.value = null
    categoryTree.value = []
    error.value = null
  }
  
  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }
  
  return {
    // State
    courses,
    currentCourse,
    coursesLoading,
    coursesTotal,
    chapters,
    currentChapter,
    chaptersLoading,
    knowledgePoints,
    currentKnowledgePoint,
    knowledgePointsLoading,
    categoryTree,
    categoriesLoading,
    error,
    
    // Computed
    activeCourses,
    currentCourseChapters,
    currentChapterKnowledgePoints,
    
    // Course methods
    fetchCourses,
    fetchAllCourses,
    fetchCourse,
    createCourse,
    updateCourse,
    deleteCourse,
    setCurrentCourse,
    
    // Chapter methods
    fetchChaptersByCourse,
    createChapter,
    updateChapter,
    deleteChapter,
    reorderChapters,
    setCurrentChapter,
    
    // Knowledge point methods
    fetchKnowledgePointsByChapter,
    createKnowledgePoint,
    updateKnowledgePoint,
    deleteKnowledgePoint,
    setCurrentKnowledgePoint,
    
    // Category methods
    fetchCategoryTree,
    createCategory,
    updateCategory,
    deleteCategory,
    moveCategory,
    
    // Utility methods
    clearState,
    clearError,
  }
}

export default useCourseManagement
