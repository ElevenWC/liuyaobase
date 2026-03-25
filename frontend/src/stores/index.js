/**
 * 六爻卦例分析系统 - Pinia Store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getGualiList, getGuali, getGualiDetail, getImageConfig } from '../api'

/**
 * 卦例Store
 */
export const useGualiStore = defineStore('guali', () => {
  // 状态
  const gualiList = ref([])
  const currentGuali = ref(null)
  const total = ref(0)
  const loading = ref(false)
  const error = ref(null)

  // 分页状态
  const pagination = ref({
    page: 1,
    pageSize: 20,
    year: null
  })

  // 获取卦例列表
  async function fetchGualiList(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await getGualiList({
        page: params.page || pagination.value.page,
        page_size: params.pageSize || pagination.value.pageSize,
        year: params.year || pagination.value.year
      })
      gualiList.value = response.items
      total.value = response.total
      pagination.value = {
        page: response.page,
        pageSize: response.page_size,
        year: params.year || null
      }
      return response
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // 获取单个卦例
  async function fetchGuali(id) {
    loading.value = true
    error.value = null
    try {
      const response = await getGuali(id)
      currentGuali.value = response
      return response
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // 获取卦例完整详情
  async function fetchGualiDetail(id) {
    loading.value = true
    error.value = null
    try {
      const response = await getGualiDetail(id)
      currentGuali.value = response
      return response
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // 清除当前卦例
  function clearCurrentGuali() {
    currentGuali.value = null
  }

  return {
    // 状态
    gualiList,
    currentGuali,
    total,
    loading,
    error,
    pagination,
    // 方法
    fetchGualiList,
    fetchGuali,
    fetchGualiDetail,
    clearCurrentGuali
  }
})

/**
 * 图片配置Store
 */
export const useImageStore = defineStore('image', () => {
  // 状态
  const config = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 获取图片存储配置
  async function fetchConfig() {
    loading.value = true
    error.value = null
    try {
      const response = await getImageConfig()
      config.value = response
      return response
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    config,
    loading,
    error,
    fetchConfig
  }
})

/**
 * 应用全局状态Store
 */
export const useAppStore = defineStore('app', () => {
  // 侧边栏折叠状态
  const sidebarCollapsed = ref(false)

  // 切换侧边栏
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return {
    sidebarCollapsed,
    toggleSidebar
  }
})
