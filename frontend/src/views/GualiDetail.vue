<script setup>
import { ref, watch, computed } from 'vue'
import { useAppStore } from '../stores/index.js'
import { fetchGualiDetail, updateGuali, deleteGuali } from '../api/index.js'
import GuaCiFloat from '../components/shared/GuaCiFloat.vue'

const store = useAppStore()

const detail = ref(null)
const loading = ref(false)
const error = ref('')

const showTianGan = ref(false)
const showLiuShen = ref(true)
const showYiMao = ref(false)
const zhiMode = ref('all')

const editingShiyou = ref(false)
const editingZhanduan = ref(false)
const editShiyou = ref('')
const editZhanduan = ref('')

const activeFloats = ref([])

const WUXING = {
  '子': '水', '丑': '土', '寅': '木', '卯': '木',
  '辰': '土', '巳': '火', '午': '火', '未': '土',
  '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

const reversedYaos = computed(() => detail.value?.yaos ? [...detail.value.yaos].reverse() : [])
const isJingGua = computed(() => detail.value?.yao_bian_code === '000000')
const hasZengshan = computed(() => detail.value?.yaos?.some(y => y.zengshan_exists))
const showZhiColumns = computed(() => zhiMode.value !== 'hide' && !isJingGua.value)

watch(() => store.currentGualiId, loadDetail, { immediate: true })

async function loadDetail() {
  if (!store.currentGualiId) return
  loading.value = true; error.value = ''
  try {
    const res = await fetchGualiDetail(store.currentGualiId)
    if (res.data.code === 200) detail.value = res.data.data
    else error.value = res.data.message || '加载失败'
  } catch { error.value = '加载失败' }
  finally { loading.value = false }
}

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

async function saveShiyou() {
  try { await updateGuali(detail.value.id, { zhanwen_shiyou: editShiyou.value }); detail.value.zhanwen_shiyou = editShiyou.value; editingShiyou.value = false }
  catch { error.value = '保存失败' }
}
async function saveZhanduan() {
  try { await updateGuali(detail.value.id, { zhanduan: editZhanduan.value }); detail.value.zhanduan = editZhanduan.value; editingZhanduan.value = false }
  catch { error.value = '保存失败' }
}
async function onDelete() {
  if (!confirm('确定删除此卦例？')) return
  try { await deleteGuali(detail.value.id); detail.value = null; store.currentGualiId = null }
  catch { error.value = '删除失败' }
}
function openGuaCi(guaCode, guaName) {
  activeFloats.value.push({ id: Date.now() + Math.random(), guaCode, guaName })
}
function closeFloat(floatId) { activeFloats.value = activeFloats.value.filter(f => f.id !== floatId) }
function fanYinText() {
  const d = detail.value
  if (!d) return ''
  const t = []
  if (d.fan_yin_yimao !== '无') t.push('易冒反吟：' + d.fan_yin_yimao)
  if (d.fan_yin_yaobian !== '无') t.push('爻变反吟：' + d.fan_yin_yaobian)
  if (d.fu_yin !== '无') t.push('伏吟：' + d.fu_yin)
  return t.length ? t.join('  ') : '反伏状态：无'
}
</script>

<template>
  <div class="guali-detail" v-if="store.currentGualiId">
    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    <template v-else-if="detail">
      <div class="top-bar">
        <span class="guali-id">卦例 #{{ detail.id }}</span>
        <button @click="onDelete" class="btn-del">删除</button>
      </div>

      <div class="gua-names">
        <span class="gua-name clickable" @click="openGuaCi(detail.ben_code, detail.ben_name || detail.ben_code)">
          本卦：{{ detail.ben_name || detail.ben_code }}
        </span>
        <span v-if="detail.zhi_name" class="gua-name clickable" style="margin-left:16px" @click="openGuaCi(detail.zhi_code, detail.zhi_name)">
          之卦：{{ detail.zhi_name }}
        </span>
      </div>

      <div class="info-section">
        <div class="info-row">
          <span class="label">占问时间：</span>{{ detail.zhanwen_time?.slice(0, 10) }}
        </div>
        <div class="info-row" @dblclick="editingShiyou = true; editShiyou = detail.zhanwen_shiyou">
          <span class="label">占问事由：</span>
          <span v-if="!editingShiyou">{{ detail.zhanwen_shiyou }}</span>
          <input v-else v-model="editShiyou" @blur="saveShiyou" @keyup.enter="saveShiyou" autofocus class="edit-input" />
        </div>
        <div class="info-row" v-if="detail.tags?.length">
          <span class="label">标签：</span><span v-for="t in detail.tags" :key="t" class="tag-badge">{{ t }}</span>
        </div>
      </div>

      <div class="info-section">
        <div class="info-row">
          <span class="label">年柱：</span>{{ detail.year_pillar }}
          <span style="margin-left:16px"><span class="label">月柱：</span>{{ detail.month_pillar }}</span>
          <span style="margin-left:16px"><span class="label">日柱：</span>{{ detail.day_pillar }}</span>
          <span style="margin-left:16px"><span class="label">旬空：</span>{{ detail.xun_kong }}</span>
        </div>
      </div>

      <div class="info-section">
        <div class="info-row">
          <span class="label">干禄：</span>{{ detail.gan_lu }}
          <span style="margin-left:16px"><span class="label">驿马：</span>{{ detail.yi_ma }}</span>
          <span style="margin-left:16px"><span class="label">羊刃：</span>{{ detail.yang_ren }}</span>
          <span style="margin-left:16px"><span class="label">桃花：</span>{{ detail.tao_hua }}</span>
        </div>
      </div>

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

      <div class="yao-card">
        <div class="yao-header">
          <span v-if="showLiuShen" class="hdr hdr-ls">六神</span>
          <span v-if="showYiMao" class="hdr hdr-ym">易冒</span>
          <span v-if="hasZengshan" class="hdr hdr-zs">增删</span>
          <span class="hdr hdr-ben">本卦</span>
          <span class="hdr hdr-line">卦象</span>
          <span class="hdr hdr-mark">动</span>
          <span class="hdr hdr-sy">世应</span>
          <template v-if="showZhiColumns">
            <span class="hdr hdr-zhi">之卦</span>
            <span class="hdr hdr-zx">卦象</span>
            <span class="hdr hdr-zsy">世应</span>
          </template>
        </div>
        <div class="yao-rows">
          <div v-for="y in reversedYaos" :key="y.yao_position"
            class="yao-row" :class="{ 'shi-row': y.ben_shi_ying === '世' }">
            <span v-if="showLiuShen" class="col col-ls">{{ y.liushen }}</span>
            <span v-if="showYiMao" class="col col-ym">{{ y.yimao_liuqin }}{{ dizhiFull(y.yimao_dizhi) }}</span>
            <span v-if="hasZengshan" class="col col-zs">
              <template v-if="y.zengshan_exists">{{ y.zengshan_liuqin }}{{ dizhiFull(y.zengshan_dizhi) }}</template>
            </span>
            <span class="col col-ben">{{ y.ben_liuqin }}{{ dizhiFull(y.ben_dizhi, y.ben_tiangan) }}</span>
            <span class="col col-line">
              <span class="yao-line" :class="{ yin: y.ben_yao_type === '阴', yang: y.ben_yao_type === '阳' }">
                <span v-if="y.ben_yao_type === '阴'" class="seg"></span>
                <span v-if="y.ben_yao_type === '阴'" class="gap"></span>
                <span v-if="y.ben_yao_type === '阴'" class="seg"></span>
              </span>
            </span>
            <span class="col col-mark">{{ yaoMark(y) }}</span>
            <span class="col col-sy">{{ y.ben_shi_ying }}</span>
            <template v-if="showZhiColumns">
              <span class="col col-zhi">
                <template v-if="zhiMode !== 'changed' || y.is_dong">{{ y.zhi_liuqin }}{{ dizhiFull(y.zhi_dizhi, y.zhi_tiangan) }}</template>
              </span>
              <span class="col col-line">
                <template v-if="zhiMode !== 'changed' || y.is_dong">
                  <span class="yao-line" :class="{ yin: y.zhi_yao_type === '阴', yang: y.zhi_yao_type === '阳' }">
                    <span v-if="y.zhi_yao_type === '阴'" class="seg"></span>
                    <span v-if="y.zhi_yao_type === '阴'" class="gap"></span>
                    <span v-if="y.zhi_yao_type === '阴'" class="seg"></span>
                  </span>
                </template>
              </span>
              <span class="col col-sy">
                <template v-if="zhiMode !== 'changed' || y.is_dong">{{ y.zhi_shi_ying }}</template>
              </span>
            </template>
          </div>
        </div>
      </div>

      <div class="info-section" @dblclick="editingZhanduan = true; editZhanduan = detail.zhanduan">
        <div class="label">占断内容：</div>
        <p v-if="!editingZhanduan" class="zhanduan-text">{{ detail.zhanduan }}</p>
        <textarea v-else v-model="editZhanduan" @blur="saveZhanduan" rows="6" autofocus class="edit-textarea" />
      </div>

      <GuaCiFloat v-for="f in activeFloats" :key="f.id" :gua-code="f.guaCode" :gua-name="f.guaName" :visible="true" @close="closeFloat(f.id)" />
    </template>
  </div>
  <div v-else class="no-selection">点击左侧卦例查看详情</div>
</template>

<style scoped>
.guali-detail { padding: var(--space-6); color: var(--color-text-primary); background: var(--color-bg-primary); min-height: 100%; }
.error-msg { color: var(--color-danger); padding: var(--space-5); }
.no-selection { text-align: center; color: var(--color-text-muted); padding: var(--space-10); }

.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.guali-id { font-size: var(--font-size-lg); font-weight: bold; color: var(--color-text-primary); }
.btn-del { padding: 4px 14px; background: var(--color-danger); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; transition: background var(--transition-fast); }
.btn-del:hover { background: var(--color-danger-hover); }

.gua-names { margin-bottom: var(--space-3); font-size: var(--font-size-md); }
.gua-name.clickable { color: var(--color-accent); cursor: pointer; border-bottom: 1px dashed var(--color-accent); }

.info-section { background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-3); margin-bottom: var(--space-3); box-shadow: var(--shadow-sm); }
.info-row { line-height: var(--line-height); }
.label { color: var(--color-text-secondary); }

.toggles { display: flex; gap: 14px; align-items: center; margin: var(--space-3) 0; padding: var(--space-2) var(--space-3); background: var(--color-bg-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-sm); }
.toggles label { display: flex; align-items: center; gap: 4px; cursor: pointer; color: var(--color-text-secondary); }
.toggles select { padding: 2px 4px; background: var(--color-bg-tertiary); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); transition: border-color var(--transition-fast); }

.yao-card {
  width: 640px; max-width: 100%;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  box-shadow: var(--shadow-sm);
  margin: var(--space-3) 0;
}
.yao-header { display: flex; align-items: center; padding: 0 0 var(--space-2) 0; border-bottom: 1px solid var(--color-border-primary); margin-bottom: var(--space-1); }
.hdr { font-size: var(--font-size-xs); color: var(--color-text-secondary); font-weight: 500; text-align: center; }
.hdr-ls { width: 44px; flex-shrink: 0; }
.hdr-ym { width: 50px; flex-shrink: 0; }
.hdr-zs { width: 50px; flex-shrink: 0; }
.hdr-ben { flex: 1; }
.hdr-line { width: 72px; flex-shrink: 0; }
.hdr-mark { width: 28px; flex-shrink: 0; }
.hdr-sy { width: 36px; flex-shrink: 0; }
.hdr-zhi { flex: 1; }
.hdr-zx { width: 72px; flex-shrink: 0; }
.hdr-zsy { width: 36px; flex-shrink: 0; }

.yao-rows { display: flex; flex-direction: column; }
.yao-row { display: flex; align-items: center; padding: 4px 0; min-height: 32px; }
.yao-row.shi-row { background: var(--color-accent-soft); border-radius: var(--radius-sm); }

.col { font-size: var(--font-size-sm); color: var(--color-text-primary); text-align: center; white-space: nowrap; }
.col-ls { width: 44px; flex-shrink: 0; color: var(--color-text-secondary); }
.col-ym { width: 50px; flex-shrink: 0; font-size: var(--font-size-xs); }
.col-zs { width: 50px; flex-shrink: 0; font-size: var(--font-size-xs); color: var(--color-accent-light); }
.col-ben { flex: 1; text-align: left; padding-left: var(--space-2); }
.col-line { width: 72px; flex-shrink: 0; display: flex; justify-content: center; }
.col-mark { width: 28px; flex-shrink: 0; font-size: var(--font-size-md); font-weight: bold; }
.col-sy { width: 36px; flex-shrink: 0; color: var(--color-accent); font-weight: bold; }
.col-zhi { flex: 1; text-align: left; padding-left: var(--space-2); }

/* yao line drawing */
.yao-line {
  display: inline-flex; align-items: center;
  width: 64px; height: 18px;
}
.yao-line.yang {
  border-top: 4px solid var(--color-text-primary);
  border-radius: 2px;
}
.yao-line.yin { justify-content: center; gap: 14px; }
.yao-line .seg {
  width: 24px; height: 0;
  border-top: 4px solid var(--color-text-primary);
  border-radius: 2px;
}
.yao-line .gap { width: 14px; }

.shi-row { background: var(--color-accent-soft); }

.zhanduan-text { white-space: pre-wrap; line-height: var(--line-height); }
.tag-badge { padding: 1px 8px; background: var(--color-badge-bg); color: var(--color-badge-text); border-radius: var(--radius-sm); font-size: var(--font-size-xs); margin-right: var(--space-1); }

.edit-input, .edit-textarea { background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-accent); border-radius: var(--radius-md); padding: var(--space-1) var(--space-2); width: 100%; }
.edit-textarea { padding: var(--space-2); min-height: 120px; }
</style>
