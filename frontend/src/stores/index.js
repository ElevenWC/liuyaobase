import { ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchTagTree } from '../api/index.js'

export const useAppStore = defineStore('app', () => {
  const currentGualiId = ref(null)
  const tagTree = ref([])
  const tagTreeLoaded = ref(false)

  function selectGuali(id) {
    currentGualiId.value = id
  }

  async function loadTagTree() {
    const res = await fetchTagTree()
    tagTree.value = res.data.data || []
    tagTreeLoaded.value = true
  }

  function refreshTagTree() {
    tagTreeLoaded.value = false
  }

  return {
    currentGualiId,
    tagTree,
    tagTreeLoaded,
    selectGuali,
    loadTagTree,
    refreshTagTree,
  }
})
