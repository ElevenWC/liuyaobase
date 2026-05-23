<script setup>
import { ref, watch, computed } from 'vue'
import { useAppStore } from '../stores/index.js'
import { fetchGualiDetail, updateGuali, deleteGuali } from '../api/index.js'
import GuaCiFloat from '../components/shared/GuaCiFloat.vue'

const store = useAppStore()

const detail = ref(null)
const loading = ref(false)
const error = ref('')

// 显示开关
const showTianGan = ref(false)
const showLiuShen = ref(true)
const showYiMao = ref(false)
const zhiMode = ref('all')

// 编辑
const editingShiyou = ref(false)
const editingZhanduan = ref(false)
const editShiyou = ref('')
const editZhanduan = ref('')

// 卦爻辞浮窗——多实例
const activeFloats = ref([])

// 地支→五行
const WUXING = {
  '子': '水', '丑': '土', '寅': '木', '卯': '木',
  '辰': '土', '巳': '火', '午': '火', '未': '土',
  '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

watch(() => store.currentGualiId, loadDetail, { immediate: true })

async function loadDetail() {
  if (!store.currentGualiId) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetchGualiDetail(store.currentGualiId)
    if (res.data.code === 200) {
      detail.value = res.data.data
    } else {
      error.value = res.data.message || '加载失败'
    }
  } catch {
    error.value = '加载失败'
  } finally {
    loading.value = false
  }
}

const reversedYaos = computed(() => {
  if (!detail.value?.yaos) return []
  return [...detail.value.yaos].reverse()
})

const isJingGua = computed(() => detail.value?.yao_bian_code === '000000')
const hasZengshan = computed(() => detail.value?.yaos?.some(y => y.zengshan_exists))
const showZhiColumns = computed(() => zhiMode.value !== 'hide' && !isJingGua.value)

function dizhiFull(dz, tg) {
  if (!dz) return ''
  const wx = WUXING[dz] || ''
  const t = (showTianGan.value && tg) ? tg : ''
  return t + dz + wx
}

function yaoMark(y) {
  if (y.is_dong && y.ben_yao_type === '阳') return '○'
  if (y.is_dong && y.ben_yao_type === '阴') return '×'
  if (y.is_an_dong) return '△'
  return ''
}

function yaoSymbol(yType) {
  return yType === '阳' ? '───' : '─ ─'
}

async function saveShiyou() {
  try {
    await updateGuali(detail.value.id, { zhanwen_shiyou: editShiyou.value })
    detail.value.zhanwen_shiyou = editShiyou.value
    editingShiyou.value = false
  } catch { error.value = '保存失败' }
}

async function saveZhanduan() {
  try {
    await updateGuali(detail.value.id, { zhanduan: editZhanduan.value })
    detail.value.zhanduan = editZhanduan.value
    editingZhanduan.value = false
  } catch { error.value = '保存失败' }
}

async function onDelete() {
  if (!confirm('确定删除此卦例？')) return
  try {
    await deleteGuali(detail.value.id)
    detail.value = null
    store.currentGualiId = null
  } catch { error.value = '删除失败' }
}

function openGuaCi(guaCode, guaName) {
  activeFloats.value.push({
    id: Date.now() + Math.random(),
    guaCode,
    guaName,
  })
}

function closeFloat(floatId) {
  activeFloats.value = activeFloats.value.filter(f => f.id !== floatId)
}

function fanYinText() {
  const d = detail.value
  if (!d) return ''
  const texts = []
  if (d.fan_yin_yimao !== '无') texts.push('易冒反吟：' + d.fan_yin_yimao)
  if (d.fan_yin_yaobian !== '无') texts.push('爻变反吟：' + d.fan_yin_yaobian)
  if (d.fu_yin !== '无') texts.push('伏吟：' + d.fu_yin)
  return texts.length ? texts.join('  ') : '反伏状态：无'
}
</script>

<template>
  <div class="guali-detail" v-if="store.currentGualiId">
    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    <template v-else-if="detail">
      <!-- 顶栏 -->
      <div class="top-bar">
        <span class="guali-id">卦例 #{{ detail.id }}</span>
        <button @click="onDelete" class="btn-del">删除</button>
      </div>

      <!-- 卦名 -->
      <div class="gua-names">
        <span class="gua-name clickable" @click="openGuaCi(detail.ben_code, detail.ben_name || detail.ben_code)">
          本卦：{{ detail.ben_name || detail.ben_code }}
        </span>
        <span v-if="detail.zhi_name" class="gua-name clickable" style="margin-left:16px" @click="openGuaCi(detail.zhi_code, detail.zhi_name)">
          之卦：{{ detail.zhi_name }}
        </span>
      </div>

      <!-- 基本信息 -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">占问时间：</span>{{ detail.zhanwen_time }}
        </div>
        <div class="info-row" @dblclick="editingShiyou = true; editShiyou = detail.zhanwen_shiyou">
          <span class="label">占问事由：</span>
          <span v-if="!editingShiyou">{{ detail.zhanwen_shiyou }}</span>
          <input v-else v-model="editShiyou" @blur="saveShiyou" @keyup.enter="saveShiyou" autofocus />
        </div>
        <div class="info-row" v-if="detail.tags?.length">
          <span class="label">标签：</span>
          <span v-for="t in detail.tags" :key="t" class="tag-badge">{{ t }}</span>
        </div>
      </div>

      <!-- 时间 -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">年柱：</span>{{ detail.year_pillar }}
          <span style="margin-left:16px"><span class="label">月柱：</span>{{ detail.month_pillar }}</span>
          <span style="margin-left:16px"><span class="label">日柱：</span>{{ detail.day_pillar }}</span>
          <span style="margin-left:16px"><span class="label">旬空：</span>{{ detail.xun_kong }}</span>
        </div>
      </div>

      <!-- 神煞 -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">干禄：</span>{{ detail.gan_lu }}
          <span style="margin-left:16px"><span class="label">驿马：</span>{{ detail.yi_ma }}</span>
          <span style="margin-left:16px"><span class="label">羊刃：</span>{{ detail.yang_ren }}</span>
          <span style="margin-left:16px"><span class="label">桃花：</span>{{ detail.tao_hua }}</span>
        </div>
      </div>

      <!-- 卦类型 -->
      <div class="info-section" v-if="detail.ben_palace">
        <div class="info-row">
          本卦：{{ detail.ben_name || detail.ben_code }}（{{ detail.ben_palace }}{{ detail.ben_palace_type }}<span v-if="detail.ben_special_type !== '普通'">·{{ detail.ben_special_type }}</span>）
          <template v-if="!isJingGua">
            <span style="margin-left:16px">
              之卦：{{ detail.zhi_name || detail.zhi_code }}（{{ detail.zhi_palace }}{{ detail.zhi_palace_type }}<span v-if="detail.zhi_special_type !== '普通'">·{{ detail.zhi_special_type }}</span>）
            </span>
          </template>
        </div>
        <div class="info-row">{{ fanYinText() }}</div>
      </div>

      <!-- 开关 -->
      <div class="toggles">
        <label><input type="checkbox" v-model="showLiuShen" /> 六神</label>
        <label><input type="checkbox" v-model="showTianGan" /> 天干</label>
        <label><input type="checkbox" v-model="showYiMao" /> 易冒</label>
        <label v-if="!isJingGua">
          之卦：
          <select v-model="zhiMode">
            <option value="all">全部</option>
            <option value="changed">仅变爻</option>
            <option value="hide">隐藏</option>
          </select>
        </label>
      </div>

      <!-- 卦象表格 -->
      <div class="yao-table-wrap">
        <table class="yao-table">
          <thead>
            <tr>
              <th v-if="showLiuShen">六神</th>
              <th v-if="showYiMao">易冒</th>
              <th v-if="hasZengshan">增删</th>
              <th>本卦</th>
              <th>卦象</th>
              <th>动</th>
              <th>世应</th>
              <th v-if="showZhiColumns">之卦</th>
              <th v-if="showZhiColumns">卦象</th>
              <th v-if="showZhiColumns">世应</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="y in reversedYaos" :key="y.yao_position" :class="{ 'shi-row': y.ben_shi_ying === '世' }">
              <td v-if="showLiuShen">{{ y.liushen }}</td>
              <td v-if="showYiMao">{{ y.yimao_liuqin }}{{ dizhiFull(y.yimao_dizhi) }}</td>
              <td v-if="hasZengshan">
                <template v-if="y.zengshan_exists">{{ y.zengshan_liuqin }}{{ dizhiFull(y.zengshan_dizhi) }}</template>
              </td>
              <td>{{ y.ben_liuqin }}{{ dizhiFull(y.ben_dizhi, y.ben_tiangan) }}</td>
              <td>{{ yaoSymbol(y.ben_yao_type) }}</td>
              <td>{{ yaoMark(y) }}</td>
              <td>{{ y.ben_shi_ying }}</td>
              <td v-if="showZhiColumns">
                <template v-if="zhiMode !== 'changed' || y.is_dong">{{ y.zhi_liuqin }}{{ dizhiFull(y.zhi_dizhi, y.zhi_tiangan) }}</template>
              </td>
              <td v-if="showZhiColumns">
                <template v-if="zhiMode !== 'changed' || y.is_dong">{{ yaoSymbol(y.zhi_yao_type) }}</template>
              </td>
              <td v-if="showZhiColumns">
                <template v-if="zhiMode !== 'changed' || y.is_dong">{{ y.zhi_shi_ying }}</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 占断 -->
      <div class="info-section" @dblclick="editingZhanduan = true; editZhanduan = detail.zhanduan">
        <div class="label">占断内容：</div>
        <p v-if="!editingZhanduan" class="zhanduan-text">{{ detail.zhanduan }}</p>
        <textarea v-else v-model="editZhanduan" @blur="saveZhanduan" rows="6" autofocus />
      </div>

      <!-- 卦爻辞浮窗（多实例） -->
      <GuaCiFloat
        v-for="f in activeFloats"
        :key="f.id"
        :gua-code="f.guaCode"
        :gua-name="f.guaName"
        :visible="true"
        @close="closeFloat(f.id)"
      />
    </template>
  </div>
  <div v-else class="no-selection">点击左侧卦例查看详情</div>
</template>

<style scoped>
.guali-detail { padding: 16px; color: #fff; background: #545a61; min-height: 100%; }
.error-msg { color: #e57373; padding: 20px; }
.no-selection { text-align: center; color: #8f969c; padding: 60px; }

.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.guali-id { font-size: 18px; font-weight: bold; }
.btn-del { padding: 4px 14px; background: #c62828; color: #fff; border: none; border-radius: 4px; cursor: pointer; }

.gua-names { margin-bottom: 10px; font-size: 16px; }
.gua-name.clickable { color: #64b5f6; cursor: pointer; border-bottom: 1px dashed #64b5f6; }

.info-section { margin-bottom: 8px; }
.info-row { line-height: 1.8; }
.label { color: #8f969c; }

.toggles { display: flex; gap: 14px; align-items: center; margin: 10px 0; padding: 6px 10px; background: #4a5058; border-radius: 4px; font-size: 13px; }
.toggles label { display: flex; align-items: center; gap: 4px; cursor: pointer; }
.toggles select { padding: 2px 4px; background: #545a61; color: #fff; border: 1px solid #666; border-radius: 3px; }

.yao-table-wrap { margin: 10px 0; }
.yao-table { border-collapse: collapse; font-size: 14px; }
.yao-table th, .yao-table td { padding: 4px 10px; text-align: center; white-space: nowrap; }
.yao-table th { color: #8f969c; font-weight: 500; font-size: 12px; border-bottom: 1px solid #666; }
.yao-table td { color: #fff; }
.shi-row { background: rgba(255,215,0,0.12); }

.zhanduan-text { white-space: pre-wrap; line-height: 1.8; }
.tag-badge { padding: 1px 8px; background: #4a6b8a; border-radius: 10px; font-size: 12px; margin-right: 4px; }
</style>
