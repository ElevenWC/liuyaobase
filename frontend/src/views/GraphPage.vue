<script setup>
import { ref, watch } from 'vue'
import { fetchGraphData } from '../api/index.js'
import NetworkGraph from '../components/shared/NetworkGraph.vue'
import GuaCiFloat from '../components/shared/GuaCiFloat.vue'
import { GUA_NAMES, GUA_CODES } from '../constants/guaNames.js'

function codeToName(code) { const i = GUA_CODES.indexOf(code); return i >= 0 ? GUA_NAMES[i] : code }

const graphType = ref('yang')
const graphData = ref({ nodes: [], edges: [] })
const loading = ref(false)

const activeFloats = ref([])
function openGuaCi(code) {
  activeFloats.value.push({ id: Date.now() + Math.random(), guaCode: code, guaName: codeToName(code) })
}
function closeFloat(id) { activeFloats.value = activeFloats.value.filter(f => f.id !== id) }

async function loadGraph() {
  loading.value = true
  try {
    const res = await fetchGraphData(graphType.value)
    if (res.data.code === 200) graphData.value = res.data.data
  } catch { /* ignore */ }
  finally { loading.value = false }
}

watch(graphType, loadGraph, { immediate: true })
</script>

<template>
  <div class="graph-page">
    <div class="graph-type-bar">
      <label :class="{ active: graphType === 'yang' }">
        <input type="radio" value="yang" v-model="graphType" /> 阳图谱（上爻为阳爻 · 32卦）
      </label>
      <label :class="{ active: graphType === 'yin' }">
        <input type="radio" value="yin" v-model="graphType" /> 阴图谱（上爻为阴爻 · 32卦）
      </label>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <NetworkGraph
      v-else-if="graphData.nodes.length"
      :nodes="graphData.nodes" :edges="graphData.edges"
      :canvas-width="1200" :canvas-height="900"
      :show-controls="true" :show-legend="true"
      @dblclick-node="openGuaCi"
    />

    <GuaCiFloat v-for="f in activeFloats" :key="f.id"
      :gua-code="f.guaCode" :gua-name="f.guaName" :visible="true"
      @close="closeFloat(f.id)" />
  </div>
</template>

<style scoped>
.graph-page { padding: var(--space-4); color: var(--color-text-primary); background: var(--color-bg-primary); min-height: 100%; }

.graph-type-bar { display: flex; gap: var(--space-4); margin-bottom: var(--space-3); justify-content: center; }
.graph-type-bar label {
  padding: 4px 16px; background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary); border-radius: var(--radius-md);
  font-size: var(--font-size-sm); color: var(--color-text-secondary); cursor: pointer;
  transition: all var(--transition-fast);
}
.graph-type-bar label.active { border-color: var(--color-accent); color: var(--color-accent-light); background: var(--color-accent-soft); }
.graph-type-bar input { display: none; }

.loading { text-align: center; padding: var(--space-10); color: var(--color-text-muted); }
</style>
