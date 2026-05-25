<script setup>
import { ref, watch } from 'vue'
import { fetchGraphData } from '../api/index.js'
import NetworkGraph from '../components/shared/NetworkGraph.vue'
import GuaCiFloat from '../components/shared/GuaCiFloat.vue'

const GUA_CODES = [
  '111111','000000','010001','001010','010111','111010','000010','010000',
  '011111','110111','000111','111000','101111','111101','000001','001000',
  '011001','100110','000011','011000','100101','101001','001000','000100',
  '100111','001111','100001','011110','010010','101101','011100','001110',
  '001111','111100','101000','000101','101011','110101','001010','010100',
  '001110','011001','111110','011111','000110','011000','010110','001011',
  '011101','101110','100100','001001','100011','011010','101100','001101',
  '011011','110110','110010','010011','110011','001100','010101','101010',
]
const GUA_NAMES = [
  '乾为天','坤为地','水雷屯','山水蒙','水天需','天水讼','地水师','水地比',
  '风天小畜','天泽履','地天泰','天地否','天火同人','火天大有','地山谦','雷地豫',
  '泽雷随','山风蛊','地泽临','风地观','火雷噬嗑','山火贲','山地剥','地雷复',
  '天雷无妄','山天大畜','山雷颐','泽风大过','坎为水','离为火','泽山咸','雷风恒',
  '天山遁','雷天大壮','火地晋','地火明夷','风火家人','火泽睽','水山蹇','雷水解',
  '山泽损','风雷益','泽天夬','天风姤','泽地萃','地风升','泽水困','水风井',
  '泽火革','火风鼎','震为雷','艮为山','风山渐','雷泽归妹','雷火丰','火山旅',
  '巽为风','兑为泽','风水涣','水泽节','风泽中孚','雷山小过','水火既济','火水未济',
]
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
