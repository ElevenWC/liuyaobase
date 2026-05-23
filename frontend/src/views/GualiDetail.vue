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
const zhiMode = ref('all') // 'changed' | 'all' | 'hide'

// 编辑状态
const editingShiyou = ref(false)
const editingZhanduan = ref(false)
const editShiyou = ref('')
const editZhanduan = ref('')

// 卦爻辞浮窗
const guaciVisible = ref(false)

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
  } catch (e) {
    error.value = '加载失败'
  } finally {
    loading.value = false
  }
}

// 爻数据——反转，首行=上爻
const reversedYaos = computed(() => {
  if (!detail.value?.yaos) return []
  return [...detail.value.yaos].reverse()
})

// 过滤之卦显示
const filteredYaos = computed(() => {
  if (zhiMode.value === 'all') return reversedYaos.value
  if (zhiMode.value === 'hide') return reversedYaos.value
  // changed only
  return reversedYaos.value.filter(y => y.is_dong)
})

function yaoMark(y) {
  if (y.is_dong && y.ben_yao_type === '阳') return '○'
  if (y.is_dong && y.ben_yao_type === '阴') return '×'
  if (y.is_an_dong) return '△'
  return ''
}

function yaoDizhi(y) {
  if (!y) return ''
  if (showTianGan.value && y.ben_tiangan) return y.ben_tiangan + y.ben_dizhi
  return y.ben_dizhi
}

function zhiDizhi(y) {
  if (!y) return ''
  if (showTianGan.value && y.zhi_tiangan) return y.zhi_tiangan + y.zhi_dizhi
  return y.zhi_dizhi
}

function isJingGua() {
  return detail.value?.yao_bian_code === '000000'
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

const benGuaName = computed(() => detail.value?.ben_palace ? detail.value.ben_code : '')
const zhiGuaName = computed(() => isJingGua() ? '' : detail.value?.zhi_code)
</script>

<template>
  <div class="guali-detail" v-if="store.currentGualiId">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    <template v-else-if="detail">
      <!-- 顶栏 -->
      <div class="top-bar">
        <span class="guali-id">卦例 #{{ detail.id }}</span>
        <div class="top-actions">
          <button @click="onDelete" class="btn-danger">删除</button>
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">占问时间：</span>
          <span>{{ detail.zhanwen_time }}</span>
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

      <!-- 时间信息 -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">年柱：</span><span>{{ detail.year_pillar }}</span>
          <span class="label" style="margin-left:16px">月柱：</span><span>{{ detail.month_pillar }}</span>
          <span class="label" style="margin-left:16px">日柱：</span><span>{{ detail.day_pillar }}</span>
          <span class="label" style="margin-left:16px">旬空：</span><span>{{ detail.xun_kong }}</span>
        </div>
      </div>

      <!-- 神煞 -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">干禄：</span><span>{{ detail.gan_lu }}</span>
          <span class="label" style="margin-left:16px">驿马：</span><span>{{ detail.yi_ma }}</span>
          <span class="label" style="margin-left:16px">羊刃：</span><span>{{ detail.yang_ren }}</span>
          <span class="label" style="margin-left:16px">桃花：</span><span>{{ detail.tao_hua }}</span>
        </div>
      </div>

      <!-- 卦类型 -->
      <div class="info-section" v-if="detail.ben_palace">
        <div class="info-row">
          <span>本卦：{{ detail.ben_palace }}{{ detail.ben_palace_type }}</span>
          <span v-if="detail.ben_special_type !== '普通'" style="margin-left:8px">({{ detail.ben_special_type }})</span>
          <span v-if="!isJingGua()" style="margin-left:16px">
            之卦：{{ detail.zhi_palace }}{{ detail.zhi_palace_type }}
            <span v-if="detail.zhi_special_type !== '普通'" style="margin-left:4px">({{ detail.zhi_special_type }})</span>
          </span>
        </div>
        <div class="info-row" v-if="detail.fan_yin_yimao !== '无' || detail.fu_yin !== '无'">
          易冒反吟：{{ detail.fan_yin_yimao }} | 爻变反吟：{{ detail.fan_yin_yaobian }} | 伏吟：{{ detail.fu_yin }}
        </div>
      </div>

      <!-- 显示开关 -->
      <div class="toggles">
        <label><input type="checkbox" v-model="showLiuShen" /> 六神</label>
        <label><input type="checkbox" v-model="showTianGan" /> 天干</label>
        <label><input type="checkbox" v-model="showYiMao" /> 易冒</label>
        <label>
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
              <th v-if="showYiMao">易冒伏神</th>
              <th>增删伏神</th>
              <th>本卦爻</th>
              <th>卦象</th>
              <th>动</th>
              <th>世应</th>
              <th v-if="zhiMode !== 'hide'">之卦爻</th>
              <th v-if="zhiMode !== 'hide'">卦象</th>
              <th v-if="zhiMode !== 'hide'">世应</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="y in filteredYaos" :key="y.yao_position">
              <td v-if="showLiuShen">{{ y.liushen }}</td>
              <td v-if="showYiMao">{{ y.yimao_liuqin }}{{ y.yimao_dizhi }}</td>
              <td>
                <template v-if="y.zengshan_exists">{{ y.zengshan_liuqin }}{{ y.zengshan_dizhi }}</template>
              </td>
              <td>{{ y.ben_liuqin }}{{ yaoDizhi(y) }}</td>
              <td>{{ y.ben_yao_type === '阳' ? '⚊' : '⚋' }}</td>
              <td>{{ yaoMark(y) }}</td>
              <td>{{ y.ben_shi_ying }}</td>
              <td v-if="zhiMode !== 'hide'">{{ y.zhi_liuqin }}{{ zhiDizhi(y) }}</td>
              <td v-if="zhiMode !== 'hide'">{{ y.zhi_yao_type === '阳' ? '⚊' : '⚋' }}</td>
              <td v-if="zhiMode !== 'hide'">{{ y.zhi_shi_ying }}</td>
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

      <!-- 卦爻辞浮窗 -->
      <GuaCiFloat
        v-if="guaciVisible"
        :gua-code="detail.ben_code"
        :gua-name="detail.ben_code"
        :visible="guaciVisible"
        @close="guaciVisible = false"
      />
    </template>
  </div>
  <div v-else class="no-selection">点击左侧卦例查看详情</div>
</template>

<style scoped>
.guali-detail { padding: 16px; }
.loading { text-align: center; padding: 40px; color: #999; }
.error-msg { color: red; padding: 20px; }
.no-selection { text-align: center; color: #999; padding: 60px; }

.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.guali-id { font-size: 18px; font-weight: bold; }
.btn-danger { padding: 6px 16px; background: #e53935; color: #fff; border: none; border-radius: 4px; cursor: pointer; }

.info-section { margin-bottom: 10px; }
.info-row { line-height: 2; }
.label { color: #666; }

.toggles { display: flex; gap: 16px; align-items: center; margin: 12px 0; padding: 8px; background: #f5f5f5; border-radius: 4px; }
.toggles label { display: flex; align-items: center; gap: 4px; font-size: 13px; cursor: pointer; }
.toggles select { padding: 2px 6px; }

.yao-table-wrap { overflow-x: auto; margin: 12px 0; }
.yao-table { border-collapse: collapse; width: 100%; font-size: 14px; }
.yao-table th, .yao-table td { border: 1px solid #ddd; padding: 6px 10px; text-align: center; white-space: nowrap; }
.yao-table th { background: #f0f0f0; font-weight: 600; }
.yao-table td { background: #fff; }

.zhanduan-text { white-space: pre-wrap; }
.tag-badge { padding: 1px 8px; background: #e8f5e9; border-radius: 10px; font-size: 12px; margin-right: 4px; }
</style>
