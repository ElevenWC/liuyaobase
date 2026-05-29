<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { importManual } from '../api/index.js'

const router = useRouter()

const TRIGRAMS = [
  { code: '111', name: '乾', symbol: '天' },
  { code: '110', name: '兑', symbol: '泽' },
  { code: '101', name: '离', symbol: '火' },
  { code: '100', name: '震', symbol: '雷' },
  { code: '011', name: '巽', symbol: '风' },
  { code: '010', name: '坎', symbol: '水' },
  { code: '001', name: '艮', symbol: '山' },
  { code: '000', name: '坤', symbol: '地' },
]

const NAMES = [
  '乾为天','坤为地','水雷屯','山水蒙','水天需','天水讼','地水师','水地比',
  '风天小畜','天泽履','地天泰','天地否','天火同人','火天大有','地山谦','雷地豫',
  '泽雷随','山风蛊','地泽临','风地观','火雷噬嗑','山火贲','山地剥','地雷复',
  '天雷无妄','山天大畜','山雷颐','泽风大过','坎为水','离为火','泽山咸','雷风恒',
  '天山遁','雷天大壮','火地晋','地火明夷','风火家人','火泽睽','水山蹇','雷水解',
  '山泽损','风雷益','泽天夬','天风姤','泽地萃','地风升','泽水困','水风井',
  '泽火革','火风鼎','震为雷','艮为山','风山渐','雷泽归妹','雷火丰','火山旅',
  '巽为风','兑为泽','风水涣','水泽节','风泽中孚','雷山小过','水火既济','火水未济',
]

function findGua(innerCode, outerCode) {
  const full = outerCode + innerCode
  const idx = CODES.indexOf(full)
  return idx >= 0 ? NAMES[idx] : null
}

// 正确的64卦代码（outer+inner格式），与NAMES一一对应
const CODES = [
  '111111','000000','010100','001010','010111','111010','000010','010000',
  '011111','111110','000111','111000','111101','101111','000001','100000',
  '110100','001011','000110','011000','101100','001101','001000','000100',
  '111100','001111','001100','110011','010010','101101','110001','100011',
  '111001','100111','101000','000101','011101','101110','010001','100010',
  '001110','011100','110111','111011','110000','000011','110010','010011',
  '110101','101011','100100','001001','011001','100110','100101','101001',
  '011011','110110','011010','010110','011110','100001','010101','101010',
]

const form = ref({
  zhanwen_time: new Date().toISOString().slice(0, 10),
  zhanwen_shiyou: '',
  zhanduan: '',
  ben_name: '',
  zhi_name: '',
})

const benMode = ref('select')
const benInner = ref('')
const benOuter = ref('')
const benManual = ref('')
const benComputed = computed(() => {
  if (benMode.value === 'select' && benInner.value && benOuter.value) return findGua(benInner.value, benOuter.value) || ''
  if (benMode.value === 'input') return benManual.value
  return ''
})

const zhiMode = ref('empty')
const zhiInner = ref('')
const zhiOuter = ref('')
const zhiManual = ref('')
const zhiComputed = computed(() => {
  if (zhiMode.value === 'empty') return ''
  if (zhiMode.value === 'select' && zhiInner.value && zhiOuter.value) return findGua(zhiInner.value, zhiOuter.value) || ''
  if (zhiMode.value === 'input') return zhiManual.value
  return ''
})

function onBenModeSwitch(mode) { benMode.value = mode; form.value.ben_name = '' }
function onZhiModeSwitch(mode) { zhiMode.value = mode; form.value.zhi_name = '' }

const submitting = ref(false)
const errorMsg = ref('')

async function submit() {
  errorMsg.value = ''
  const t = form.value.zhanwen_time

  const benName = benComputed.value
  if (!t || !form.value.zhanwen_shiyou || !benName) { errorMsg.value = '占问时间、占问事由、本卦为必填项'; return }
  if (!NAMES.includes(benName)) { errorMsg.value = '本卦名不在64卦中: ' + benName; return }

  const zhiName = zhiComputed.value
  if (zhiName && !NAMES.includes(zhiName)) { errorMsg.value = '之卦名不在64卦中: ' + zhiName; return }

  submitting.value = true
  try {
    const res = await importManual({ zhanwen_time: t, zhanwen_shiyou: form.value.zhanwen_shiyou, zhanduan: form.value.zhanduan, ben_name: benName, zhi_name: zhiName || undefined })
    if (res.data.code === 200) {
      router.push('/')
    } else {
      errorMsg.value = res.data.message || '导入失败'
    }
  } catch (e) { errorMsg.value = e.response?.data?.message || '导入失败' }
  finally { submitting.value = false }
}
</script>

<template>
  <div class="guali-input">
    <h2>手动导入卦例</h2>
    <form @submit.prevent="submit" class="input-form">
      <label class="field-label"><span class="label-text">占问时间 <span class="required">*</span></span>
        <input type="date" v-model="form.zhanwen_time" />
      </label>
      <label class="field-label"><span class="label-text">占问事由 <span class="required">*</span></span>
        <input v-model="form.zhanwen_shiyou" placeholder="例：上证指数05.22走势" />
      </label>
      <label>占断内容
        <textarea v-model="form.zhanduan" rows="4" placeholder="可选" />
      </label>

      <fieldset>
        <legend>本卦 <span class="required">*</span></legend>
        <div class="mode-switch">
          <label><input type="radio" value="select" v-model="benMode" @change="onBenModeSwitch('select')" />二级选择</label>
          <label><input type="radio" value="input" v-model="benMode" @change="onBenModeSwitch('input')" />手动输入</label>
        </div>
        <template v-if="benMode === 'select'">
          <div class="gua-select-row">
            <label>外卦
              <select v-model="benOuter"><option value="">-- 选外卦 --</option>
                <option v-for="g in TRIGRAMS" :key="'bout'+g.code" :value="g.code">{{ g.symbol }}（{{ g.name }}）</option>
              </select>
            </label>
            <label>内卦
              <select v-model="benInner"><option value="">-- 选内卦 --</option>
                <option v-for="g in TRIGRAMS" :key="'bin'+g.code" :value="g.code">{{ g.symbol }}（{{ g.name }}）</option>
              </select>
            </label>
          </div>
          <p v-if="benComputed" class="computed">→ {{ benComputed }}</p>
          <p v-else-if="benInner || benOuter" class="hint">请完整选择内外卦</p>
        </template>
        <input v-else v-model="benManual" placeholder="输入卦名，如 天火同人" />
      </fieldset>

      <fieldset>
        <legend>之卦</legend>
        <div class="mode-switch">
          <label><input type="radio" value="empty" v-model="zhiMode" @change="onZhiModeSwitch('empty')" />静卦</label>
          <label><input type="radio" value="select" v-model="zhiMode" @change="onZhiModeSwitch('select')" />二级选择</label>
          <label><input type="radio" value="input" v-model="zhiMode" @change="onZhiModeSwitch('input')" />手动输入</label>
        </div>
        <template v-if="zhiMode === 'select'">
          <div class="gua-select-row">
            <label>外卦
              <select v-model="zhiOuter"><option value="">-- 选外卦 --</option>
                <option v-for="g in TRIGRAMS" :key="'zout'+g.code" :value="g.code">{{ g.symbol }}（{{ g.name }}）</option>
              </select>
            </label>
            <label>内卦
              <select v-model="zhiInner"><option value="">-- 选内卦 --</option>
                <option v-for="g in TRIGRAMS" :key="'zin'+g.code" :value="g.code">{{ g.symbol }}（{{ g.name }}）</option>
              </select>
            </label>
          </div>
          <p v-if="zhiComputed" class="computed">→ {{ zhiComputed }}</p>
          <p v-else-if="zhiInner || zhiOuter" class="hint">请完整选择内外卦</p>
        </template>
        <input v-if="zhiMode === 'input'" v-model="zhiManual" placeholder="输入卦名，如 风火家人" />
      </fieldset>

      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <button type="submit" :disabled="submitting">{{ submitting ? '提交中...' : '提交' }}</button>
    </form>
  </div>
</template>

<style scoped>
.guali-input { max-width: 560px; margin: var(--space-5) auto; color: var(--color-text-primary); }
h2 { color: var(--color-text-primary); margin-bottom: var(--space-4); }
.input-form { display: flex; flex-direction: column; gap: var(--space-4); }
label { display: flex; flex-direction: column; gap: var(--space-1); font-weight: 500; color: var(--color-text-secondary); }
.field-label .label-text { display: inline; }
.required { color: var(--color-danger); }
input, textarea, select {
  padding: var(--space-2); border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md); background: var(--color-bg-input);
  color: var(--color-text-primary); font-size: var(--font-size-base);
  font-family: var(--font-family); color-scheme: dark;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(1); }
input::placeholder, textarea::placeholder { color: var(--color-text-muted); }
input:focus, textarea:focus, select:focus { border-color: var(--color-accent); box-shadow: var(--shadow-glow); }
select option { background: var(--color-bg-secondary); color: var(--color-text-primary); }
input[type="radio"] { accent-color: var(--color-accent); }
.error { color: var(--color-danger); }
.hint { color: var(--color-text-muted); }
.computed { color: var(--color-accent-light); font-weight: bold; }
button[type="submit"] {
  padding: var(--space-2) var(--space-6); background: var(--color-accent-gradient);
  color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer;
  font-size: var(--font-size-base); box-shadow: var(--shadow-md);
  transition: opacity var(--transition-fast), box-shadow var(--transition-fast);
}
button[type="submit"]:hover:not(:disabled) { opacity: 0.9; box-shadow: var(--shadow-glow); }
button[type="submit"]:disabled { opacity: 0.5; cursor: not-allowed; }
fieldset { border: 1px solid var(--color-border-primary); border-radius: var(--radius-lg); padding: var(--space-3); background: var(--color-bg-secondary); }
legend { font-weight: bold; color: var(--color-text-primary); }
.mode-switch { display: flex; gap: var(--space-4); margin-bottom: var(--space-2); }
.mode-switch label { flex-direction: row; font-weight: normal; color: var(--color-text-secondary); cursor: pointer; }
.gua-select-row { display: flex; gap: var(--space-3); }
.gua-select-row label { flex: 1; }
</style>
