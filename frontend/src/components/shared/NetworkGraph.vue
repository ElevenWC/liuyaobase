<script setup>
/**
 * NetworkGraph — 卦关系网络图（共享组件，供 BagongPage / GraphPage 复用）
 *
 * 纯 SVG + 自建力导向物理引擎，零外部依赖。
 * 改造自用户旧项目的 NetworkGraph.vue，适配 liuyaobase CSS 变量体系。
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  nodes: { type: Array, required: true },
  edges: { type: Array, required: true },
  /** 画布宽度，默认 1200（全屏），小窗版传 350 */
  canvasWidth: { type: Number, default: 1200 },
  /** 画布高度 */
  canvasHeight: { type: Number, default: 900 },
  /** 是否显示缩放控件 */
  showControls: { type: Boolean, default: true },
  /** 是否显示图例 */
  showLegend: { type: Boolean, default: true },
  /** 初始缩放比例，默认 1.2（参考基准） */
  initialScale: { type: Number, default: 1.2 },
})

const emit = defineEmits(['select-node', 'dblclick-node'])

const ELEMENT_COLORS = { 金: '#FFD700', 木: '#228B22', 水: '#1E90FF', 火: '#FF4500', 土: '#8B4513' }

// ── 内部节点（含物理状态） ──
const simNodes = ref([])
const selectedNode = ref(null)
const alwaysShowLabels = ref(false)
const scale = ref(props.initialScale)
let animationFrameId = null
let stableFrames = 0

const nodePositionMap = computed(() => {
  const map = new Map()
  for (const n of simNodes.value) map.set(n.id, { x: n.x, y: n.y })
  return map
})

function isConnectedToSelected(nodeId) {
  if (!selectedNode.value) return false
  return props.edges.some(
    e => (e.source === selectedNode.value && e.target === nodeId) ||
         (e.target === selectedNode.value && e.source === nodeId)
  )
}

function getChangeType(targetNodeId) {
  if (!selectedNode.value) return ''
  const edge = props.edges.find(
    e => e.source === selectedNode.value && e.target === targetNodeId
  )
  return edge ? edge.type : ''
}

function getNodeColor(node) {
  if (selectedNode.value === node.id) return '#e94560'
  return ELEMENT_COLORS[node.element] || '#888'
}

function getNodeSize(node) {
  if (selectedNode.value === node.id) return 12
  if (isConnectedToSelected(node.id)) return 10
  return 8
}

function zoomIn() { scale.value = Math.min(3, scale.value + 0.2) }
function zoomOut() { scale.value = Math.max(0.3, scale.value - 0.2) }
function resetZoom() { scale.value = props.initialScale }

const svgContainerRef = ref(null)
function handleWheel(event) {
  if (!svgContainerRef.value) return
  const target = event.target
  if (!svgContainerRef.value.contains(target)) return
  event.preventDefault()
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  scale.value = Math.min(3, Math.max(0.3, scale.value + delta))
}

// ── 力导向模拟 ──
// 参考基准：1200×900 画布，力参数按当前画布等比缩放
const REF_BASE = 900

function initSimulation() {
  const cx = props.canvasWidth / 2
  const cy = props.canvasHeight / 2
  simNodes.value = props.nodes.map((n, i) => {
    const angle = (i / props.nodes.length) * 2 * Math.PI
    const radius = Math.min(cx, cy) * 0.6
    return {
      id: n.id, name: n.name, element: n.element,
      x: cx + Math.cos(angle) * radius,
      y: cy + Math.sin(angle) * radius,
      vx: 0, vy: 0,
    }
  })
  stableFrames = 0
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  simulate()
}

function simulate() {
  const cx = props.canvasWidth / 2
  const cy = props.canvasHeight / 2
  const scale = Math.min(props.canvasWidth, props.canvasHeight) / REF_BASE
  const idealDist = 80 * scale
  // 斥力不缩放——保持绝对像素范围防止节点在密集图谱中挤在一起
  const repelRange = 150
  const repelRangeSq = repelRange * repelRange

  let maxVelocity = 0

  for (const node of simNodes.value) {
    let fx = 0, fy = 0

    // 向心力
    fx += (cx - node.x) * 0.001
    fy += (cy - node.y) * 0.001

    // 节点间斥力
    for (const other of simNodes.value) {
      if (other.id === node.id) continue
      const dx = node.x - other.x
      const dy = node.y - other.y
      const distSq = dx * dx + dy * dy
      if (distSq < repelRangeSq && distSq > 0) {
        const dist = Math.sqrt(distSq)
        const force = (repelRange - dist) / repelRange * 1.0
        fx += (dx / dist) * force
        fy += (dy / dist) * force
      }
    }

    // 弹簧力
    for (const edge of props.edges) {
      let other = null
      if (edge.source === node.id) other = simNodes.value.find(n => n.id === edge.target)
      else if (edge.target === node.id) other = simNodes.value.find(n => n.id === edge.source)
      if (other) {
        const dx = other.x - node.x
        const dy = other.y - node.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist > 0) {
          const springForce = (dist - idealDist) * 0.01
          fx += (dx / dist) * springForce
          fy += (dy / dist) * springForce
        }
      }
    }

    node.vx += fx; node.vy += fy
    node.vx *= 0.85; node.vy *= 0.85
    node.x += node.vx; node.y += node.vy
    node.x = Math.max(50, Math.min(props.canvasWidth - 50, node.x))
    node.y = Math.max(50, Math.min(props.canvasHeight - 50, node.y))

    const v = Math.sqrt(node.vx * node.vx + node.vy * node.vy)
    if (v > maxVelocity) maxVelocity = v
  }

  if (maxVelocity < 0.05) {
    stableFrames++
    if (stableFrames > 120) return
  } else {
    stableFrames = 0
  }
  animationFrameId = requestAnimationFrame(simulate)
}

watch(() => props.nodes, () => { initSimulation() }, { immediate: true })

onMounted(() => {
  window.addEventListener('wheel', handleWheel, { passive: false })
})

onUnmounted(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('wheel', handleWheel)
})
</script>

<template>
  <div class="network-graph">
    <div v-if="showControls" class="graph-controls">
      <div class="zoom-controls">
        <button class="zoom-btn" @click="zoomOut" title="缩小">−</button>
        <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
        <button class="zoom-btn" @click="zoomIn" title="放大">+</button>
        <button class="zoom-btn" @click="resetZoom" title="重置">⟲</button>
      </div>
      <label class="label-toggle">
        <input v-model="alwaysShowLabels" type="checkbox" />
        <span>卦名常驻</span>
      </label>
    </div>

    <div class="svg-wrapper">
      <svg
        :width="canvasWidth" :height="canvasHeight"
        ref="svgContainerRef" class="graph-svg" :style="{ transform: `scale(${scale})` }"
        @click="selectedNode = null"
      >
        <!-- 边 -->
        <line
          v-for="edge in edges" :key="`${edge.source}-${edge.target}`"
          :x1="nodePositionMap.get(edge.source)?.x"
          :y1="nodePositionMap.get(edge.source)?.y"
          :x2="nodePositionMap.get(edge.target)?.x"
          :y2="nodePositionMap.get(edge.target)?.y"
          :stroke="selectedNode && (edge.source === selectedNode || edge.target === selectedNode) ? 'rgba(233,69,96,0.8)' : 'rgba(100,100,100,0.2)'"
          :stroke-width="selectedNode && (edge.source === selectedNode || edge.target === selectedNode) ? 2 : 1"
          class="graph-edge"
        />

        <!-- 节点 -->
        <circle
          v-for="node in simNodes" :key="node.id"
          :cx="node.x" :cy="node.y"
          :r="getNodeSize(node)"
          :fill="getNodeColor(node)"
          class="graph-node"
          @click.stop="selectedNode = node.id; emit('select-node', node.id)"
          @dblclick.stop="emit('dblclick-node', node.id)"
        >
          <title>{{ node.name }}（{{ node.element }}）</title>
        </circle>

        <!-- 标签：常驻模式 -->
        <template v-if="alwaysShowLabels">
          <text v-for="node in simNodes" :key="'lbl-'+node.id"
            :x="node.x" :y="node.y - 12" text-anchor="middle"
            class="graph-label graph-label--small">{{ node.name }}</text>
        </template>

        <!-- 标签：选中模式 -->
        <template v-else-if="selectedNode">
          <text
            :x="nodePositionMap.get(selectedNode).x"
            :y="nodePositionMap.get(selectedNode).y - 15"
            text-anchor="middle" class="graph-label graph-label--selected"
          >{{ simNodes.find(n => n.id === selectedNode)?.name }}</text>

          <template v-for="node in simNodes" :key="'rel-'+node.id">
            <text v-if="isConnectedToSelected(node.id)"
              :x="node.x" :y="node.y - 12" text-anchor="middle"
              class="graph-label graph-label--related">{{ node.name }}</text>
            <text v-if="isConnectedToSelected(node.id)"
              :x="(node.x + nodePositionMap.get(selectedNode).x) / 2"
              :y="(node.y + nodePositionMap.get(selectedNode).y) / 2 - 5"
              text-anchor="middle" class="graph-label graph-label--change"
            >{{ getChangeType(node.id) }}</text>
          </template>
        </template>
      </svg>
    </div>

    <div v-if="showLegend" class="graph-legend">
      <span class="legend-title">五行</span>
      <span v-for="(color, name) in ELEMENT_COLORS" :key="name" class="legend-item">
        <i class="legend-dot" :style="{ background: color }"></i>{{ name }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.network-graph { display: flex; flex-direction: column; align-items: center; gap: var(--space-2); }
.graph-controls { display: flex; align-items: center; gap: var(--space-3); }
.zoom-controls { display: flex; align-items: center; gap: var(--space-1); padding: 2px 6px; background: var(--color-bg-tertiary); border-radius: var(--radius-md); border: 1px solid var(--color-border-primary); }
.zoom-btn { width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; background: var(--color-bg-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); color: var(--color-text-primary); font-size: 14px; cursor: pointer; }
.zoom-btn:hover { background: var(--color-accent); border-color: var(--color-accent); }
.zoom-level { min-width: 40px; text-align: center; font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.label-toggle { display: flex; align-items: center; gap: 4px; font-size: var(--font-size-xs); color: var(--color-text-secondary); cursor: pointer; }
.label-toggle input { accent-color: var(--color-accent); }

.svg-wrapper { overflow: hidden; display: flex; justify-content: center; align-items: center; }
.graph-svg { cursor: grab; transform-origin: center center; transition: transform 0.1s ease-out; }
.graph-svg:active { cursor: grabbing; }
.graph-edge { transition: stroke var(--transition-fast), stroke-width var(--transition-fast); }
.graph-node { cursor: pointer; transition: r var(--transition-fast), fill var(--transition-fast); }
.graph-node:hover { filter: brightness(1.2); }

.graph-label { font-size: 11px; fill: var(--color-text-primary); pointer-events: none; }
.graph-label--small { font-size: 9px; fill: var(--color-text-secondary); opacity: 0.8; }
.graph-label--selected { font-size: 13px; font-weight: 600; fill: #e94560; }
.graph-label--related { font-size: 12px; font-weight: 500; fill: #ffa500; }
.graph-label--change { font-size: 10px; fill: #4CAF50; font-weight: 500; }

.graph-legend { display: flex; align-items: center; gap: var(--space-2); padding: 3px 8px; background: var(--color-bg-secondary); border-radius: var(--radius-md); }
.legend-title { font-size: var(--font-size-xs); font-weight: 600; color: var(--color-text-primary); }
.legend-item { display: flex; align-items: center; gap: 2px; font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
</style>
