<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchGualiDetail, fetchHugua } from '../api/index.js'
import GuaCiFloat from '../components/shared/GuaCiFloat.vue'

const route = useRoute()

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

// ── 状态 ──
const gualiIdInput = ref('')
const customGuaName = ref('')
const loading = ref(false)
const error = ref('')

// ben: { code, name, hugua: {code,name,palace,element}, source_indices }
const benResult = ref(null)
const zhiResult = ref(null)
const zhiEmptyReason = ref('') // 'jingle' | 'custom' | ''

const activeFloats = ref([])
function openGuaCi(code, name) { activeFloats.value.push({ id: Date.now() + Math.random(), guaCode: code, guaName: name }) }
function closeFloat(id) { activeFloats.value = activeFloats.value.filter(f => f.id !== id) }

// ── 爻线渲染 ──
function yaoType(code, pos) { return code[5 - pos] === '1' ? '阳' : '阴' }
// 互卦来源爻位高亮：pos 0-5，2-3-4 为内卦（蓝），3-4-5 为外卦（绿）
function yaoHighlightClass(pos) {
  // pos: 0=初爻..5=上爻，但显示从上到下，所以模板用 5-pos
  // 这里接收模板中传入的 pos (0=初爻)
  if (pos >= 1 && pos <= 3) return 'hl-inner' // 二三四爻→内卦
  if (pos >= 2 && pos <= 4) return 'hl-outer' // 三四五爻→外卦
  return ''
}

// ── 主逻辑 ──
async function onLoad() {
  const id = parseInt(gualiIdInput.value)
  if (!id) return
  loading.value = true; error.value = ''; benResult.value = null; zhiResult.value = null; zhiEmptyReason.value = ''
  try {
    const res = await fetchGualiDetail(id)
    if (res.data.code !== 200) { error.value = res.data.message; return }
    const d = res.data.data
    const benCode = d.ben_code
    const benName = d.ben_name || codeToName(benCode)
    const zhiCode = d.zhi_code
    const zhiName = d.zhi_name || codeToName(zhiCode)
    const yaoBian = d.yao_bian_code || '000000'

    // 调用互卦 API
    const huguaRes = await fetchHugua(benCode, zhiCode)
    if (huguaRes.data.code !== 200) { error.value = huguaRes.data.message; return }
    const hd = huguaRes.data.data

    benResult.value = { code: benCode, name: benName, hugua: hd.ben_hugua }

    if (yaoBian === '000000') {
      zhiEmptyReason.value = 'jingle'
    } else {
      zhiResult.value = { code: zhiCode, name: zhiName, hugua: hd.zhi_hugua }
    }
  } catch { error.value = '加载失败' }
  finally { loading.value = false }
}

function onCustomSelect() {
  const code = nameToCode(customGuaName.value)
  if (!code) return
  loading.value = true; error.value = ''; benResult.value = null; zhiResult.value = null; zhiEmptyReason.value = ''
  fetchHugua(code).then(res => {
    if (res.data.code === 200) {
      benResult.value = { code, name: customGuaName.value, hugua: res.data.data.ben_hugua }
      zhiEmptyReason.value = 'custom'
    }
  }).catch(() => { error.value = '加载失败' })
  .finally(() => { loading.value = false })
}

// ── 路由参数 ──
import { watch } from 'vue'
watch(() => route.query.guali_id, (val) => {
  if (val) { gualiIdInput.value = val; onLoad() }
}, { immediate: true })
</script>

<template>
  <div class="hugua-page">
    <!-- 顶部输入栏 -->
    <div class="top-input-bar">
      <div class="input-group">
        <label>卦例编号</label>
        <input v-model="gualiIdInput" type="number" placeholder="输入卦例 ID" @keyup.enter="onLoad" />
        <button @click="onLoad">加载</button>
      </div>
      <div class="input-group">
        <label>自定义卦名</label>
        <select v-model="customGuaName" @change="onCustomSelect">
          <option value="">-- 选择卦 --</option>
          <option v-for="name in GUA_NAMES" :key="name" :value="name">{{ name }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="status">加载中...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <!-- 双列 -->
    <div v-else class="hugua-cols">
      <!-- 本卦互卦 -->
      <div class="hugua-card" v-if="benResult">
        <div class="card-title">本卦互卦</div>
        <div class="card-body">
          <div class="gua-section">
            <span class="gua-name clickable" @click="openGuaCi(benResult.code, benResult.name)">{{ benResult.name }}</span>
            <span class="gua-code">{{ benResult.code }}</span>
            <div class="yao-display">
              <div v-for="pos in 6" :key="pos"
                class="yao-line" :class="[yaoType(benResult.code, pos - 1), yaoHighlightClass(pos - 1)]">
                <span v-if="yaoType(benResult.code, pos - 1) === '阳'" class="yang-bar"></span>
                <template v-else>
                  <span class="seg"></span><span class="seg-gap"></span><span class="seg"></span>
                </template>
              </div>
            </div>
          </div>
          <div class="arrow-section">
            <span class="big-arrow">→</span>
            <span class="hint-text">二三四爻为内<br>三四五爻为外</span>
          </div>
          <div class="gua-section">
            <span class="gua-name clickable" @click="openGuaCi(benResult.hugua.code, benResult.hugua.name)">{{ benResult.hugua.name }}</span>
            <span class="gua-code">{{ benResult.hugua.code }}</span>
            <div class="yao-display">
              <div v-for="pos in 6" :key="pos"
                class="yao-line" :class="yaoType(benResult.hugua.code, pos - 1)">
                <span v-if="yaoType(benResult.hugua.code, pos - 1) === '阳'" class="yang-bar"></span>
                <template v-else>
                  <span class="seg"></span><span class="seg-gap"></span><span class="seg"></span>
                </template>
              </div>
            </div>
          </div>
        </div>
        <div class="card-info">
          {{ benResult.hugua.palace }} · {{ benResult.hugua.element }}
        </div>
      </div>

      <!-- 之卦互卦 -->
      <div class="hugua-card" v-if="zhiResult">
        <div class="card-title">之卦互卦</div>
        <div class="card-body">
          <div class="gua-section">
            <span class="gua-name clickable" @click="openGuaCi(zhiResult.code, zhiResult.name)">{{ zhiResult.name }}</span>
            <span class="gua-code">{{ zhiResult.code }}</span>
            <div class="yao-display">
              <div v-for="pos in 6" :key="pos"
                class="yao-line" :class="[yaoType(zhiResult.code, pos - 1), yaoHighlightClass(pos - 1)]">
                <span v-if="yaoType(zhiResult.code, pos - 1) === '阳'" class="yang-bar"></span>
                <template v-else>
                  <span class="seg"></span><span class="seg-gap"></span><span class="seg"></span>
                </template>
              </div>
            </div>
          </div>
          <div class="arrow-section">
            <span class="big-arrow">→</span>
          </div>
          <div class="gua-section">
            <span class="gua-name clickable" @click="openGuaCi(zhiResult.hugua.code, zhiResult.hugua.name)">{{ zhiResult.hugua.name }}</span>
            <span class="gua-code">{{ zhiResult.hugua.code }}</span>
            <div class="yao-display">
              <div v-for="pos in 6" :key="pos"
                class="yao-line" :class="yaoType(zhiResult.hugua.code, pos - 1)">
                <span v-if="yaoType(zhiResult.hugua.code, pos - 1) === '阳'" class="yang-bar"></span>
                <template v-else>
                  <span class="seg"></span><span class="seg-gap"></span><span class="seg"></span>
                </template>
              </div>
            </div>
          </div>
        </div>
        <div class="card-info">
          {{ zhiResult.hugua.palace }} · {{ zhiResult.hugua.element }}
        </div>
      </div>

      <!-- 之卦为空状态 -->
      <div class="hugua-card empty" v-if="zhiEmptyReason">
        <div class="card-title">之卦互卦</div>
        <div class="card-empty-text">
          <template v-if="zhiEmptyReason === 'jingle'">静卦无之卦</template>
          <template v-else>自定义模式无之卦</template>
        </div>
      </div>

      <!-- 初始空状态 -->
      <div class="hugua-card placeholder" v-if="!benResult && !loading && !error">
        <div class="card-title">本卦互卦</div>
        <div class="card-empty-text">输入卦例编号或选择卦名</div>
      </div>
    </div>

    <GuaCiFloat v-for="f in activeFloats" :key="f.id"
      :gua-code="f.guaCode" :gua-name="f.guaName" :visible="true"
      @close="closeFloat(f.id)" />
  </div>
</template>

<style scoped>
.hugua-page { display: flex; flex-direction: column; align-items: center; padding: var(--space-4); color: var(--color-text-primary); background: var(--color-bg-primary); min-height: 100%; }

.top-input-bar { display: flex; gap: var(--space-5); margin-bottom: var(--space-4); padding: var(--space-3); background: var(--color-bg-secondary); border-radius: var(--radius-lg); align-self: stretch; }
.input-group { display: flex; align-items: center; gap: var(--space-2); }
.input-group label { font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.input-group input { padding: 3px 8px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); width: 100px; font-size: var(--font-size-sm); -moz-appearance: textfield; }
.input-group input::-webkit-outer-spin-button,
.input-group input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.input-group select { padding: 3px 6px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-sm); }
.input-group button { padding: 3px 14px; background: var(--color-accent); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--font-size-sm); }
.input-group button:hover { background: var(--color-accent-dark); }

.status { text-align: center; padding: var(--space-5); color: var(--color-text-muted); font-size: var(--font-size-sm); }
.status.error { color: var(--color-danger); }

.hugua-cols { display: flex; gap: var(--space-4); }
.hugua-card { flex: 1; background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-4); box-shadow: var(--shadow-sm); }
.hugua-card.empty { opacity: 0.5; }
.hugua-card.placeholder { opacity: 0.4; }
.card-title { font-size: var(--font-size-md); font-weight: 600; color: var(--color-accent-light); margin-bottom: var(--space-3); }
.card-body { display: flex; align-items: flex-start; justify-content: center; gap: var(--space-4); }
.card-info { text-align: center; margin-top: var(--space-2); font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.card-empty-text { text-align: center; padding: var(--space-8); color: var(--color-text-muted); font-size: var(--font-size-md); }

.gua-section { display: flex; flex-direction: column; align-items: center; gap: var(--space-1); }
.gua-name { font-size: var(--font-size-md); font-weight: bold; }
.gua-code { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.clickable { cursor: pointer; }
.clickable:hover { color: var(--color-accent-light); }

.arrow-section { display: flex; flex-direction: column; align-items: center; gap: 2px; padding-top: var(--space-5); }
.big-arrow { font-size: 24px; color: var(--color-text-muted); }
.hint-text { font-size: 10px; color: var(--color-text-muted); text-align: center; line-height: 1.4; }

/* ── 卦象爻线（复用 GualiDetail 渲染方式） ── */
.yao-display { display: flex; flex-direction: column; gap: 2px; }
.yao-line {
  display: inline-flex; align-items: center; justify-content: center;
  width: 64px; height: 14px; border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.yang-bar { width: 100%; height: 4px; background: var(--color-text-primary); border-radius: 2px; }
.yao-line.yin { gap: 0; }
.seg { width: 26px; height: 4px; background: var(--color-text-primary); border-radius: 2px; }
.seg-gap { width: 8px; }

/* 互卦来源爻位高亮 */
.yao-line.hl-inner { background: rgba(99, 102, 241, 0.15); }
.yao-line.hl-outer { background: rgba(34, 197, 94, 0.15); }
</style>
