/**
 * 六爻卦例分析系统 - API调用模块
 */
import axios from 'axios'

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

// =============================================================================
// 卦例相关API
// =============================================================================

/**
 * 创建卦例
 * @param {Object} data - 卦例数据
 * @returns {Promise<Object>} 创建的卦例
 */
export function createGuali(data) {
  return apiClient.post('/api/guali', data)
}

/**
 * 获取卦例列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 卦例列表
 */
export function getGualiList(params = {}) {
  return apiClient.get('/api/guali', { params })
}

/**
 * 获取单个卦例
 * @param {number} id - 卦例ID
 * @returns {Promise<Object>} 卦例详情
 */
export function getGuali(id) {
  return apiClient.get(`/api/guali/${id}`)
}

/**
 * 获取卦例完整详情
 * @param {number} id - 卦例ID
 * @returns {Promise<Object>} 卦例完整详情
 */
export function getGualiDetail(id) {
  return apiClient.get(`/api/guali/${id}/detail`)
}

/**
 * 更新卦例
 * @param {number} id - 卦例ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>} 更新后的卦例
 */
export function updateGuali(id, data) {
  return apiClient.put(`/api/guali/${id}`, data)
}

/**
 * 删除卦例
 * @param {number} id - 卦例ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteGuali(id) {
  return apiClient.delete(`/api/guali/${id}`)
}

/**
 * CSV导入卦例
 * @param {File} file - CSV文件
 * @returns {Promise<Object>} 导入结果
 */
export function importCsv(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/api/guali/import-csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// =============================================================================
// 图片相关API
// =============================================================================

/**
 * 获取图片存储配置
 * @returns {Promise<Object>} 图片存储配置
 */
export function getImageConfig() {
  return apiClient.get('/api/images/config')
}

/**
 * 上传图片
 * @param {File} file - 图片文件
 * @returns {Promise<Object>} 上传结果
 */
export function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/api/images/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取图片URL
 * @param {string} filename - 图片文件名
 * @returns {string} 图片URL
 */
export function getImageUrl(filename) {
  if (!filename) return ''
  return `${API_BASE_URL}/api/images/${filename}`
}

/**
 * 获取图片列表
 * @returns {Promise<Object>} 图片列表
 */
export function getImageList() {
  return apiClient.get('/api/images')
}

/**
 * 删除图片
 * @param {string} filename - 图片文件名
 * @returns {Promise<Object>} 删除结果
 */
export function deleteImage(filename) {
  return apiClient.delete(`/api/images/${filename}`)
}

// =============================================================================
// 系统相关API
// =============================================================================

/**
 * 健康检查
 * @returns {Promise<Object>} 健康状态
 */
export function healthCheck() {
  return apiClient.get('/health')
}

// =============================================================================
// 检索相关API
// =============================================================================

/**
 * 复杂检索
 * @param {Object} params - 检索参数
 * @param {Array} params.conditions - 检索条件列表
 * @param {string} params.logic - 逻辑运算符 (and/or)
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise<Object>} 检索结果
 */
export function searchGuali(params) {
  return apiClient.post('/api/search', params)
}

/**
 * 获取可检索字段列表
 * @returns {Promise<Object>} 字段列表
 */
export function getSearchFields() {
  return apiClient.get('/api/search/fields')
}

// =============================================================================
// 占验情况相关API
// =============================================================================

/**
 * 标注占验情况
 * @param {Object} data - 标注数据
 * @param {number} data.guali_id - 卦例ID
 * @param {string} data.status - 占验状态（应验、模糊、不验）
 * @param {string} [data.note] - 备注说明
 * @returns {Promise<Object>} 标注结果
 */
export function annotateYanqing(data) {
  return apiClient.post('/api/yanqing/annotate', data)
}

/**
 * 获取指定卦例的占验情况
 * @param {number} gualiId - 卦例ID
 * @returns {Promise<Object>} 占验情况
 */
export function getYanqing(gualiId) {
  return apiClient.get(`/api/yanqing/${gualiId}`)
}

/**
 * 更新占验情况标注
 * @param {number} gualiId - 卦例ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>} 更新后的占验情况
 */
export function updateYanqing(gualiId, data) {
  return apiClient.put(`/api/yanqing/${gualiId}`, data)
}

/**
 * 删除占验情况标注
 * @param {number} gualiId - 卦例ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteYanqing(gualiId) {
  return apiClient.delete(`/api/yanqing/${gualiId}`)
}

/**
 * 批量获取多个卦例的占验情况
 * @param {Array<number>} gualiIds - 卦例ID列表
 * @returns {Promise<Array>} 占验情况列表
 */
export function getYanqingBatch(gualiIds) {
  return apiClient.post('/api/yanqing/batch', { guali_ids: gualiIds })
}

/**
 * 按状态获取占验情况列表
 * @param {string} status - 占验状态（应验、模糊、不验）
 * @returns {Promise<Array>} 占验情况列表
 */
export function getYanqingByStatus(status) {
  return apiClient.get(`/api/yanqing/status/${status}`)
}

/**
 * 获取占验情况统计信息
 * @returns {Promise<Object>} 统计信息
 */
export function getYanqingStatistics() {
  return apiClient.get('/api/yanqing/statistics')
}

/**
 * 导出所有占验情况数据
 * @returns {Promise<Object>} 导出数据
 */
export function exportYanqing() {
  return apiClient.get('/api/yanqing/export')
}

/**
 * 导入占验情况数据
 * @param {string} jsonData - JSON格式的占验数据
 * @param {boolean} [merge=true] - 是否合并现有数据
 * @returns {Promise<Object>} 导入结果
 */
export function importYanqing(jsonData, merge = true) {
  return apiClient.post('/api/yanqing/import', {
    json_data: jsonData,
    merge
  })
}

// =============================================================================
// 股票相关API
// =============================================================================

/**
 * 搜索股票
 * @param {string} keyword - 搜索关键词（股票名称或代码）
 * @returns {Promise<Object>} 搜索结果
 */
export function searchStock(keyword) {
  return apiClient.get('/api/stock/search', { params: { keyword } })
}

/**
 * 获取K线数据
 * @param {Object} params - 查询参数
 * @param {string} params.code - 股票代码
 * @param {string} params.start_date - 开始日期 (YYYY-MM-DD)
 * @param {string} params.end_date - 结束日期 (YYYY-MM-DD)
 * @param {string} [params.adjust='qfq'] - 复权类型
 * @returns {Promise<Object>} K线数据
 */
export function getKlineData(params) {
  return apiClient.get('/api/stock/kline', { params })
}

/**
 * 获取分时数据
 * @param {string} code - 股票代码
 * @returns {Promise<Object>} 分时数据
 */
export function getIntradayData(code) {
  return apiClient.get('/api/stock/intraday', { params: { code } })
}

/**
 * 获取股票名称匹配的卦例
 * @param {Object} params - 查询参数
 * @param {string} params.name - 股票名称
 * @param {string} [params.start_date] - 开始日期
 * @param {string} [params.end_date] - 结束日期
 * @returns {Promise<Object>} 卦例映射数据
 */
export function getGualiMapping(params) {
  return apiClient.get('/api/stock/guali-mapping', { params })
}

/**
 * 清除股票数据缓存
 * @returns {Promise<Object>} 清除结果
 */
export function clearStockCache() {
  return apiClient.get('/api/stock/cache/clear')
}

/**
 * 获取股票模块状态
 * @returns {Promise<Object>} 状态信息
 */
export function getStockStatus() {
  return apiClient.get('/api/stock/status')
}

export default {
  createGuali,
  getGualiList,
  getGuali,
  getGualiDetail,
  updateGuali,
  deleteGuali,
  importCsv,
  getImageConfig,
  uploadImage,
  getImageUrl,
  getImageList,
  deleteImage,
  healthCheck,
  searchGuali,
  getSearchFields,
  annotateYanqing,
  getYanqing,
  updateYanqing,
  deleteYanqing,
  getYanqingBatch,
  getYanqingByStatus,
  getYanqingStatistics,
  exportYanqing,
  importYanqing,
  // 股票相关
  searchStock,
  getKlineData,
  getIntradayData,
  getGualiMapping,
  clearStockCache,
  getStockStatus
}
