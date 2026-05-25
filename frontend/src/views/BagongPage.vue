<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchGualiDetail, fetchBagong, fetchGraphData } from '../api/index.js'
import GuaCiFloat from '../components/shared/GuaCiFloat.vue'
import NetworkGraph from '../components/shared/NetworkGraph.vue'

const route = useRoute()
const router = useRouter()

// ── 64 卦数据 ──
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

function nameToCode(name) { const i = GUA_NAMES.indexOf(name); return i >= 0 ? GUA_CODES[i] : '' }
function codeToName(code) { const i = GUA_CODES.indexOf(code); return i >= 0 ? GUA_NAMES[i] : code }

// ── 行状态（4 行） ──
// 每行: { mode: 'guali'|'custom'|'empty', gualiId: null, guaCode: '', guaName: '', data: null, loading: false, error: '' }
function makeRow() {
  return { mode: 'empty', gualiId: null, guaCode: '', guaName: '', data: null, loading: false, error: '' }
}

const rows = ref([makeRow(), makeRow(), makeRow(), makeRow()])

// 当前编辑的行索引（用于自定义选择器）
const editingRowIndex = ref(0)
const customGuaName = ref('')

// GuaCiFloat 管理
const activeFloats = ref([])

function openGuaCi(guaCode, guaName) {
  activeFloats.value.push({ id: Date.now() + Math.random(), guaCode, guaName })
}
function closeFloat(id) { activeFloats.value = activeFloats.value.filter(f => f.id !== id) }

// ── 图谱数据 ──
const graphData = ref({ nodes: [], edges: [] })
const graphLoading = ref(false)

async function loadGraph(guaCode) {
  if (!guaCode) return
  const graphType = guaCode[5] === '1' ? 'yang' : 'yin'
  graphLoading.value = true
  try {
    const res = await fetchGraphData(graphType)
    if (res.data.code === 200) graphData.value = res.data.data
  } catch { /* ignore */ }
  finally { graphLoading.value = false }
}

// ── 行级操作 ──
async function loadRowByGuali(rowIndex, gualiId) {
  const row = rows.value[rowIndex]
  row.loading = true; row.error = ''
  try {
    const res = await fetchGualiDetail(gualiId)
    if (res.data.code !== 200) { row.error = res.data.message; return }
    const d = res.data.data
    row.gualiId = gualiId
    row.guaCode = d.ben_code
    row.guaName = d.ben_name || codeToName(d.ben_code)
    row.mode = 'guali'
    await loadRowBagong(rowIndex, row.guaCode)
  } catch { row.error = '加载卦例失败' }
  finally { row.loading = false }
}

async function loadRowBagong(rowIndex, guaCode) {
  const row = rows.value[rowIndex]
  row.loading = true; row.error = ''
  try {
    const res = await fetchBagong(guaCode)
    if (res.data.code === 200) row.data = res.data.data
    else row.error = res.data.message
  } catch { row.error = '加载八宫变化失败' }
  finally { row.loading = false }
}

function setRowCustom(rowIndex, guaName) {
  const code = nameToCode(guaName)
  if (!code) return
  const row = rows.value[rowIndex]
  row.mode = 'custom'; row.gualiId = null; row.guaCode = code; row.guaName = guaName
  loadRowBagong(rowIndex, code)
  if (rowIndex === 0) loadGraph(code)
}

// ── 卦例编号入口（加载 guali_detail 一次，填充第1行+第2行） ──
const gualiIdInput = ref('')

async function onGualiLoad() {
  const id = parseInt(gualiIdInput.value)
  if (!id) return

  rows.value[0].loading = true; rows.value[0].error = ''
  try {
    const res = await fetchGualiDetail(id)
    if (res.data.code !== 200) { rows.value[0].error = res.data.message; return }
    const d = res.data.data

    // 第1行：本卦
    const r0 = rows.value[0]
    r0.mode = 'guali'; r0.gualiId = id
    r0.guaCode = d.ben_code; r0.guaName = d.ben_name || codeToName(d.ben_code)
    await loadGraph(r0.guaCode)
    await loadRowBagong(0, r0.guaCode)

    // 第2行：之卦
    const yaoBian = d.yao_bian_code || '000000'
    if (yaoBian === '000000') {
      rows.value[1].mode = 'custom_empty'; rows.value[1].error = ''
      return
    }
    if (yaoBian[5] === '1') {
      rows.value[1].error = '此卦上爻为动爻，不可用八宫变化'
      return
    }
    const zhiCode = d.zhi_code
    const zhiName = d.zhi_name || codeToName(zhiCode)
    rows.value[1].mode = 'guali'; rows.value[1].guaCode = zhiCode; rows.value[1].guaName = zhiName
    await loadRowBagong(1, zhiCode)
  } catch { rows.value[0].error = '加载卦例失败' }
  finally { rows.value[0].loading = false }
}

// ── 图谱交互 ──
function onGraphSelect(nodeId) {
  // 单击高亮（NetworkGraph 内部处理），这里不需要额外逻辑
}

function onGraphDblClick(nodeId) {
  // 双击填充自定义行：优先第3行，再第4行
  const name = codeToName(nodeId)
  for (let i = 2; i <= 3; i++) {
    if (rows.value[i].mode === 'empty' || rows.value[i].mode === 'custom_empty') {
      setRowCustom(i, name)
      return
    }
  }
}

// ── 路由参数 ──
watch(() => route.query.guali_id, (val) => {
  if (val) { gualiIdInput.value = val; onGualiLoad() }
}, { immediate: true })

// ── 清除行 ──
function clearRow(rowIndex) {
  const empty = makeRow()
  rows.value[rowIndex] = empty
  // 清除第1行时，图谱跟随下一个有内容的行
  if (rowIndex === 0) {
    const next = rows.value.find(r => r.mode !== 'empty' && r.guaCode)
    if (next) loadGraph(next.guaCode)
  }
}

// ── 卦象渲染辅助 ──
function yaoType(code, pos) { return code[5 - pos] === '1' ? '阳' : '阴' }
</script>

<template>
  <div class="bagong-page">
    <!-- 顶部输入栏 -->
    <div class="top-input-bar">
      <div class="input-group">
        <label>卦例编号</label>
        <input v-model="gualiIdInput" type="number" placeholder="输入卦例 ID" @keyup.enter="onGualiLoad" />
        <button @click="onGualiLoad">加载</button>
      </div>
      <div class="input-group">
        <label>自定义卦名</label>
        <select v-model="customGuaName" @change="setRowCustom(editingRowIndex, customGuaName)">
          <option value="">-- 选择卦 --</option>
          <option v-for="name in GUA_NAMES" :key="name" :value="name">{{ name }}</option>
        </select>
        <label style="margin-left:8px">填入行</label>
        <select v-model.number="editingRowIndex">
          <option :value="0">第1行（本卦）</option>
          <option :value="1">第2行（之卦）</option>
          <option :value="2">第3行（自定义1）</option>
          <option :value="3">第4行（自定义2）</option>
        </select>
      </div>
    </div>

    <div class="main-area">
      <!-- 左侧：4 行八宫变化 -->
      <div class="rows-area">
        <div v-for="(row, ri) in rows" :key="ri" class="bagong-row"
          :class="{ 'row-empty': row.mode === 'empty' || row.mode === 'custom_empty' }">
          <div class="row-label">
            <template v-if="ri === 0">本卦</template>
            <template v-else-if="ri === 1">之卦</template>
            <template v-else>自定义{{ ri - 1 }}</template>
            <button v-if="row.mode !== 'empty'" class="row-clear-btn" @click="clearRow(ri)" title="清除此行的卦">×</button>
          </div>

          <div v-if="row.loading" class="row-status">加载中...</div>

          <template v-else-if="row.data">
            <div class="row-header">
              <span class="row-gua-name clickable" @click="openGuaCi(row.guaCode, row.guaName)">
                {{ row.guaName }} <small>{{ row.guaCode }}</small>
              </span>
              <span class="row-gua-info" v-if="row.data.ben_gua">
                {{ row.data.ben_gua.palace }} · {{ row.data.ben_gua.element }}
              </span>
            </div>
            <div class="steps-row">
              <!-- 本卦 -->
              <div class="step-card" @click="openGuaCi(row.guaCode, row.guaName)">
                <div class="step-yao">
                  <div v-for="pos in 6" :key="pos" class="yao-line"
                    :class="yaoType(row.guaCode, pos - 1) === '阳' ? 'yang' : 'yin'">
                    <span v-if="yaoType(row.guaCode, pos - 1) === '阴'" class="seg"></span>
                    <span v-if="yaoType(row.guaCode, pos - 1) === '阴'" class="gap"></span>
                    <span v-if="yaoType(row.guaCode, pos - 1) === '阴'" class="seg"></span>
                  </div>
                </div>
                <span class="step-name">{{ row.guaName }}</span>
                <span class="step-type">本卦</span>
              </div>

              <span class="arrow">→</span>

              <!-- 七变 -->
              <template v-for="(step, si) in row.data.steps" :key="si">
                <div class="step-card" @click="openGuaCi(step.code, step.name)">
                  <div class="step-yao">
                    <div v-for="pos in 6" :key="pos" class="yao-line"
                      :class="yaoType(step.code, pos - 1) === '阳' ? 'yang' : 'yin'">
                      <span v-if="yaoType(step.code, pos - 1) === '阴'" class="seg"></span>
                      <span v-if="yaoType(step.code, pos - 1) === '阴'" class="gap"></span>
                      <span v-if="yaoType(step.code, pos - 1) === '阴'" class="seg"></span>
                    </div>
                  </div>
                  <span class="step-name">{{ step.name }}</span>
                  <span class="step-type">{{ step.type }}</span>
                </div>
                <span v-if="si < 6" class="arrow">→</span>
              </template>
            </div>
          </template>

          <div v-else-if="row.mode === 'custom_empty'" class="row-status hint">
            双击图谱节点填充
          </div>
          <div v-else-if="row.error" class="row-status error">{{ row.error }}</div>
          <div v-else class="row-status">等待输入</div>
        </div>
      </div>

      <!-- 右侧：图谱小窗 -->
      <div class="graph-mini">
        <div class="graph-mini-header">
          <span>网络图谱</span>
          <router-link to="/jiegua/graph" class="graph-expand" title="放大">🔍</router-link>
        </div>
        <NetworkGraph
          v-if="graphData.nodes.length"
          :nodes="graphData.nodes" :edges="graphData.edges"
          :canvas-width="340" :canvas-height="380"
          :show-controls="false" :show-legend="true"
          @select-node="onGraphSelect" @dblclick-node="onGraphDblClick"
        />
        <div v-else class="graph-empty">加载图谱中...</div>
      </div>
    </div>

    <!-- GuaCiFloat 浮窗 -->
    <GuaCiFloat v-for="f in activeFloats" :key="f.id"
      :gua-code="f.guaCode" :gua-name="f.guaName" :visible="true"
      @close="closeFloat(f.id)" />
  </div>
</template>

<style scoped>
.bagong-page { padding: var(--space-4); color: var(--color-text-primary); background: var(--color-bg-primary); min-height: 100%; }

/* 顶部输入栏 */
.top-input-bar { display: flex; gap: var(--space-5); margin-bottom: var(--space-4); padding: var(--space-3); background: var(--color-bg-secondary); border-radius: var(--radius-lg); }
.input-group { display: flex; align-items: center; gap: var(--space-2); }
.input-group label { font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.input-group input { padding: 3px 8px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); width: 100px; font-size: var(--font-size-sm); }
.input-group input[type="number"] { -moz-appearance: textfield; }
.input-group input[type="number"]::-webkit-outer-spin-button,
.input-group input[type="number"]::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.input-group select { padding: 3px 6px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-sm); }
.input-group button { padding: 3px 14px; background: var(--color-accent); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--font-size-sm); }
.input-group button:hover { background: var(--color-accent-dark); }

/* 主区域 */
.main-area { display: flex; gap: var(--space-3); }
.rows-area { flex: 1; display: flex; flex-direction: column; gap: var(--space-3); min-width: 0; max-width: 55%; }

/* 行 */
.bagong-row { background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-3); box-shadow: var(--shadow-sm); }
.bagong-row.row-empty { opacity: 0.5; }
.row-label { display: flex; align-items: center; gap: var(--space-2); font-size: var(--font-size-sm); font-weight: 600; color: var(--color-accent-light); margin-bottom: var(--space-1); }
.row-clear-btn { width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 12px; cursor: pointer; line-height: 1; }
.row-clear-btn:hover { border-color: var(--color-danger); color: var(--color-danger); }
.row-header { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-2); }
.row-gua-name { font-size: var(--font-size-md); font-weight: bold; }
.row-gua-name small { font-weight: normal; color: var(--color-text-muted); margin-left: 4px; }
.row-gua-info { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.row-status { padding: var(--space-2); font-size: var(--font-size-sm); color: var(--color-text-muted); }
.row-status.error { color: var(--color-danger); }
.row-status.hint { color: var(--color-accent-light); font-style: italic; }

/* 七步变化 */
.steps-row { display: flex; align-items: center; gap: 4px; overflow-x: auto; padding: var(--space-2) 0; }
.step-card { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 4px 6px; background: var(--color-bg-tertiary); border-radius: var(--radius-md); cursor: pointer; transition: box-shadow var(--transition-fast); flex-shrink: 0; min-width: 56px; }
.step-card:hover { box-shadow: var(--shadow-glow); }
.step-yao { display: flex; flex-direction: column; gap: 1px; }
.step-name { font-size: var(--font-size-xs); font-weight: 500; }
.step-type { font-size: 10px; color: var(--color-text-muted); }
.arrow { color: var(--color-text-muted); font-size: var(--font-size-sm); flex-shrink: 0; }
.clickable { cursor: pointer; }
.clickable:hover { color: var(--color-accent-light); }

/* 图谱小窗 */
.graph-mini { flex: 1; min-width: 320px; background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-2); box-shadow: var(--shadow-sm); }
.graph-mini-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-1); padding: 0 var(--space-1); }
.graph-mini-header span { font-size: var(--font-size-sm); font-weight: 600; }
.graph-expand { font-size: 16px; text-decoration: none; }
.graph-expand:hover { transform: scale(1.2); }
.graph-empty { text-align: center; padding: var(--space-5); color: var(--color-text-muted); font-size: var(--font-size-sm); }

/* ── 卦象爻线 ── */
.yao-line {
  display: inline-flex; align-items: center; justify-content: center;
  width: 40px; height: 10px;
}
.yao-line.yang::before {
  content: ''; display: block;
  width: 100%; height: 3px;
  background: var(--color-text-primary); border-radius: 2px;
}
.yao-line.yin { gap: 4px; }
.yao-line .seg {
  width: 18px; height: 3px;
  background: var(--color-text-primary); border-radius: 2px;
}
.yao-line .gap { width: 0; }
</style>
