import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    console.error('[API]', msg)
    return Promise.reject(error)
  },
)

// ── 卦例 ──────────────────────────────────────

export function fetchGualiList(params) {
  // params: { page, page_size, keyword?, tag_id? }
  return api.get('/guali', { params })
}

export function fetchGualiDetail(id) {
  return api.get(`/guali/${id}`)
}

export function updateGuali(id, data) {
  return api.put(`/guali/${id}`, data)
}

export function deleteGuali(id) {
  return api.delete(`/guali/${id}`)
}

export function deleteGualiBatch(ids) {
  return api.delete('/guali/batch', { data: { ids } })
}

export function addGualiTag(gualiId, tagId) {
  return api.post(`/guali/${gualiId}/tags`, { tag_id: tagId })
}

export function removeGualiTag(gualiId, tagId) {
  return api.delete(`/guali/${gualiId}/tags/${tagId}`)
}

// ── 标签 ──────────────────────────────────────

export function fetchTagTree() {
  return api.get('/tags')
}

export function createTag(data) {
  return api.post('/tags', data)
}

export function updateTag(id, data) {
  return api.put(`/tags/${id}`, data)
}

export function deleteTag(id) {
  return api.delete(`/tags/${id}`)
}

export function reorderTags(ids) {
  return api.post('/tags/reorder', { ids })
}

export function fetchGualiByTag(tagId, params) {
  return api.get(`/tags/${tagId}/guali`, { params })
}

// ── 导入 ──────────────────────────────────────

export function importJson(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/import/json', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function importManual(data) {
  return api.post('/import/manual', data)
}

export function fetchImportStatus() {
  return api.get('/import/status')
}

// ── 解卦 ──────────────────────────────────────

export function fetchBagong(guaCode) {
  return api.get(`/jiegua/bagong/${guaCode}`)
}

export function fetchHugua(guaCode, zhiCode) {
  return api.get(`/jiegua/hugua/${guaCode}`, { params: zhiCode ? { zhi_code: zhiCode } : {} })
}

export function fetchGraphData(graphType) {
  return api.get(`/jiegua/graph/${graphType}`)
}

// ── 检索 ──────────────────────────────────────

export function fetchSearchResults(body) {
  return api.post('/search', body)
}

export function fetchExport(body, fmt = 'csv') {
  return api.post('/search/export', body, { params: { fmt }, responseType: 'blob' })
}

// ── 干支日历 ──────────────────────────────────

export function fetchCalendar(year, month) {
  return api.get('/jiegua/calendar', { params: { year, month } })
}

// ── 卦爻辞 ────────────────────────────────────

export function fetchGuaci(code) {
  return api.get(`/jiegua/guaci/${code}`)
}

export default api
