<script setup>
import { ref, watch, computed } from 'vue'
import { useAppStore } from '../stores/index.js'
import { fetchGualiDetail, updateGuali, deleteGuali, fetchTagTree, addGualiTag, removeGualiTag } from '../api/index.js'
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
const saving = ref(false)

const activeFloats = ref([])

// 标签编辑
const showTagEditor = ref(false)
const tagTree = ref([])
const editingTags = ref([])

async function loadTagTree() {
  try { const r = await fetchTagTree(); tagTree.value = r.data.data || [] }
  catch { /* ok */ }
}

function openTagEditor() {
  loadTagTree()
  editingTags.value = detail.value?.tags ? [...detail.value.tags] : []
  showTagEditor.value = true
}

function isTagSelected(name) { return editingTags.value.includes(name) }

async function toggleTag(name) {
  const tag = findTagByName(name)
  if (!tag) return

  if (isTagSelected(name)) {
    // 移除
    await removeGualiTag(detail.value.id, tag.id)
    detail.value.tags = detail.value.tags.filter(t => t !== name)
    editingTags.value = editingTags.value.filter(t => t !== name)
  } else {
    // 添加二级标签时，去掉同组一级标签
    if (tag.parent_id) {
      const tree = store.tagTree.length ? store.tagTree : tagTree.value
      const l1 = tree.find(n => n.id === tag.parent_id)
      if (l1 && detail.value.tags.includes(l1.name)) {
        await removeGualiTag(detail.value.id, l1.id)
        detail.value.tags = detail.value.tags.filter(t => t !== l1.name)
        editingTags.value = editingTags.value.filter(t => t !== l1.name)
      }
    }
    await addGualiTag(detail.value.id, tag.id)
    if (!detail.value.tags.includes(name)) detail.value.tags.push(name)
    editingTags.value.push(name)
  }
}

const TAG_COLORS = ['#6E78C6','#9B7ED4','#CF7A97','#C49B4A','#4DA87A','#5F8EC0','#C46B6B','#4D9F99']

function tagColor(node) {
  // 用一级标签 ID 取模，颜色稳定不随顺序变化
  const tree = store.tagTree.length ? store.tagTree : tagTree.value
  const root = _findRootTag(tree, node)
  return TAG_COLORS[(root?.id || 0) % TAG_COLORS.length]
}

function _findRootTag(nodes, node) {
  // node 本身可能就是一/二级标签节点；返回它所属的一级标签
  for (const n of nodes) {
    if (n.id === node.id) return n
    if (n.children?.some(c => c.id === node.id)) return n
    const found = _findRootTag(n.children || [], node)
    if (found) return found
  }
  return null
}

// 显示标签：有同组二级则隐藏一级
function showTag(name) {
  const tree = store.tagTree.length ? store.tagTree : tagTree.value
  const tag = _findTagInTree(tree, name)
  if (!tag) return true
  if (tag.parent_id) return true
  const l1 = tree.find(n => n.id === tag.id)
  const children = l1?.children || []
  return !children.some(c => detail.value?.tags?.includes(c.name))
}

function tagBadgeColor(name) {
  const tree = store.tagTree.length ? store.tagTree : tagTree.value
  const tag = _findTagInTree(tree, name)
  if (!tag) return TAG_COLORS[0]
  const parent = tag.parent_id ? tree.find(n => n.id === tag.parent_id) : tag
  return parent ? tagColor(parent) : TAG_COLORS[0]
}

function _findTagInTree(nodes, name) {
  for (const n of nodes) {
    if (n.name === name) return n
    if (n.children?.length) { const r = _findTagInTree(n.children, name); if (r) return r }
  }
  return null
}

function findTagByName(name) {
  const tree = store.tagTree.length ? store.tagTree : tagTree.value
  return _findTagInTree(tree, name)
}

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
    if (!store.tagTree.length) await loadTagTree()
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

const isEditing = computed(() => editingShiyou.value || editingZhanduan.value)

function toggleEdit() {
  if (isEditing.value) {
    if (editingShiyou.value) saveShiyou()
    if (editingZhanduan.value) saveZhanduan()
  } else {
    editingShiyou.value = true; editShiyou.value = detail.value.zhanwen_shiyou
    editingZhanduan.value = true; editZhanduan.value = detail.value.zhanduan
  }
}
function onDblClickShiyou() { if (!editingShiyou.value) { editingShiyou.value = true; editShiyou.value = detail.value.zhanwen_shiyou } }
function onDblClickZhanduan() { if (!editingZhanduan.value) { editingZhanduan.value = true; editZhanduan.value = detail.value.zhanduan } }

async function saveShiyou() {
  if (saving.value) return; saving.value = true
  try { await updateGuali(detail.value.id, { zhanwen_shiyou: editShiyou.value }); detail.value.zhanwen_shiyou = editShiyou.value; editingShiyou.value = false }
  catch { error.value = '保存失败' }
  finally { saving.value = false }
}
async function saveZhanduan() {
  if (saving.value) return; saving.value = true
  try { await updateGuali(detail.value.id, { zhanduan: editZhanduan.value }); detail.value.zhanduan = editZhanduan.value; editingZhanduan.value = false }
  catch { error.value = '保存失败' }
  finally { saving.value = false }
}
async function onDelete() {
  if (!confirm('确定删除此卦例？')) return
  try { await deleteGuali(detail.value.id); detail.value = null; store.currentGualiId = null }
  catch (e) { error.value = '删除失败：' + (e.response?.data?.message || '未知错误') }
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
        <span class="top-shiyou" @dblclick="onDblClickShiyou">
          <template v-if="!editingShiyou">{{ detail.zhanwen_shiyou }}</template>
          <input v-else v-model="editShiyou" @blur="saveShiyou" @keyup.enter="saveShiyou" autofocus class="edit-input" />
        </span>
        <div class="top-right">
          <span class="guali-id">#{{ detail.id }}</span>
          <div class="btn-edit-wrap">
            <button @click="toggleEdit" class="btn-edit">{{ isEditing ? '保存' : '编辑' }}</button>
            <span class="btn-edit-tip">直接双击文本或者点击按钮后进行占问事由和占断编辑</span>
          </div>
          <button class="btn-jiegua" title="解卦（v0.5 实现）" disabled>解卦</button>
          <button @click="onDelete" class="btn-del">删除</button>
        </div>
      </div>

      <div class="info-section">
        <div class="info-row">
          <span class="label">占问时间：</span><span class="time-bold">{{ detail.zhanwen_time?.slice(0, 10) }}</span>
        </div>
        <div class="info-row">
          <span class="label">标签：</span>
          <template v-for="t in detail.tags" :key="t">
            <span v-if="showTag(t)" class="tag-badge" :style="{ background: tagBadgeColor(t) }">{{ t }}</span>
          </template>
          <span class="tag-add-btn" @click="openTagEditor">
            +
            <span class="btn-edit-tip">点击管理标签：选中=关联，再次点击=移除</span>
          </span>
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

      <!-- 反伏状态 -->
      <div class="info-section" v-if="detail.ben_palace">
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
        <!-- 卦名卡片行（与下方卦象列对齐） -->
        <div class="gua-cards-row">
          <span v-if="showLiuShen" class="col col-ls"></span>
          <span v-if="showYiMao" class="col col-ym"></span>
          <span v-if="hasZengshan" class="col col-zs"></span>
          <div class="gua-info-card gua-ben clickable" @click="openGuaCi(detail.ben_code, detail.ben_name || detail.ben_code)">
            <span class="gua-info-name">{{ detail.ben_name || detail.ben_code }}</span>
            <span class="gua-info-detail">{{ detail.ben_palace }}{{ detail.ben_palace_type }}<template v-if="detail.ben_special_type !== '普通'">·{{ detail.ben_special_type }}</template></span>
          </div>
          <span class="col col-mark"></span>
          <span class="col col-sy"></span>
          <template v-if="showZhiColumns">
            <div class="gua-info-card gua-zhi clickable" @click="openGuaCi(detail.zhi_code, detail.zhi_name)">
              <span class="gua-info-name">{{ detail.zhi_name }}</span>
              <span class="gua-info-detail">{{ detail.zhi_palace }}{{ detail.zhi_palace_type }}<template v-if="detail.zhi_special_type !== '普通'">·{{ detail.zhi_special_type }}</template></span>
            </div>
            <span class="col col-sy"></span>
          </template>
        </div>
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

      <div class="info-section" @dblclick="onDblClickZhanduan">
        <div class="label">占断内容：</div>
        <p v-if="!editingZhanduan" class="zhanduan-text">{{ detail.zhanduan }}</p>
        <textarea v-else v-model="editZhanduan" @blur="saveZhanduan" rows="6" autofocus class="edit-textarea" />
      </div>

      <!-- 标签编辑弹窗 -->
      <div v-if="showTagEditor" class="tag-editor-overlay" @click.self="showTagEditor = false">
        <div class="tag-editor">
          <div class="tag-editor-header">
            <span>编辑标签</span><button @click="showTagEditor = false">&times;</button>
          </div>
          <div class="tag-editor-body">
            <div v-for="node in tagTree" :key="node.id" class="tag-tree-item" :style="{ paddingLeft: '0' }">
              <div class="tag-row" :class="{ selected: isTagSelected(node.name) }" @click="toggleTag(node.name)">
                <span class="tag-badge-dot" :style="{ background: tagColor(node) }"></span>
                {{ node.name }}
              </div>
              <div v-for="c in node.children" :key="c.id" class="tag-row child" :style="{ paddingLeft: '16px' }" :class="{ selected: isTagSelected(c.name) }" @click="toggleTag(c.name)">
                <span class="tag-badge-dot" :style="{ background: tagColor(node) }"></span>
                {{ c.name }}
              </div>
            </div>
            <p v-if="!tagTree.length" class="hint">暂无标签，请先在标签管理页创建</p>
          </div>
        </div>
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
.top-shiyou { font-size: var(--font-size-lg); font-weight: bold; color: var(--color-text-primary); flex: 1; }
.top-right { display: flex; align-items: center; gap: var(--space-3); }
.guali-id { font-size: var(--font-size-base); color: var(--color-text-muted); font-weight: 500; }
.btn-del { padding: 3px 12px; background: var(--color-danger); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--font-size-sm); transition: background var(--transition-fast); }
.btn-del:hover { background: var(--color-danger-hover); }
.btn-jiegua { padding: 3px 12px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); cursor: not-allowed; font-size: var(--font-size-sm); opacity: 0.6; }
.btn-edit-wrap { position: relative; display: inline-flex; }
.btn-edit { padding: 3px 12px; background: var(--color-accent); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--font-size-sm); transition: background var(--transition-fast); }
.btn-edit:hover { background: var(--color-accent-dark); }
.btn-edit-tip { display: none; position: absolute; top: 110%; right: 0; width: 220px; padding: 6px 10px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); font-size: var(--font-size-xs); border-radius: var(--radius-sm); border: 1px solid var(--color-border-primary); white-space: normal; z-index: 100; }
.btn-edit-wrap:hover .btn-edit-tip { display: block; }

.time-bold { font-weight: bold; }

.info-section { background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-3); margin-bottom: var(--space-3); box-shadow: var(--shadow-sm); }
.info-row { line-height: var(--line-height); }
.label { color: var(--color-text-secondary); }

.toggles { display: flex; gap: 14px; align-items: center; margin: var(--space-3) 0; padding: var(--space-2) var(--space-3); background: var(--color-bg-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-sm); }
.toggles label { display: flex; align-items: center; gap: 4px; cursor: pointer; color: var(--color-text-secondary); }
.toggles select { padding: 2px 4px; background: var(--color-bg-tertiary); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); transition: border-color var(--transition-fast); }

.gua-cards-row {
  display: flex; align-items: stretch;
  padding-bottom: var(--space-3); margin-bottom: var(--space-2);
  border-bottom: 1px dashed var(--color-border-primary);
}
.gua-cards-row .col { visibility: hidden; }
.gua-info-card {
  background: var(--color-bg-secondary); border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3); box-shadow: var(--shadow-sm);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border: 2px solid transparent; cursor: pointer; flex-shrink: 0;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.gua-ben { width: 147px; margin-left: 36px;}
.gua-zhi { width: 147px; margin-left: 2px;}
.gua-info-card:hover { border-color: var(--color-accent); box-shadow: var(--shadow-glow); }
.gua-info-name { font-size: var(--font-size-md); font-weight: bold; color: var(--color-text-primary); }
.gua-info-detail { font-size: var(--font-size-xs); color: var(--color-text-secondary); margin-top: 2px; }

/* 卦爻列对齐 */
.hdr-ben, .col-ben { width: 75px; }
.hdr-zhi, .col-zhi { width: 75px; }
.hdr-line, .col-line { width: 72px; }
.hdr-zx, .col-line.zx { width: 72px; }
.hdr-mark, .col-mark { width: 28px; }
.hdr-sy, .col-sy { width: 36px; }
.hdr-zsy, .col-zsy { width: 36px; }

.yao-card {
  width: fit-content; min-width: 360px; max-width: 100%;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  box-shadow: var(--shadow-sm);
  margin: var(--space-3) 0;
}
.yao-header { display: flex; align-items: center; padding: 0 0 var(--space-2) 0; border-bottom: 1px solid var(--color-border-primary); margin-bottom: var(--space-1); }
.hdr { font-size: var(--font-size-xs); color: var(--color-text-secondary); font-weight: 500; text-align: center; flex-shrink: 0; }
.hdr-ls { width: 44px; }
.hdr-ym { width: 50px; }
.hdr-zs { width: 56px; }

.yao-rows { display: flex; flex-direction: column; }
.yao-row { display: flex; align-items: center; padding: 4px 0; min-height: 34px; }
.yao-row.shi-row { background: var(--color-accent-soft); border-radius: var(--radius-sm); }

.col { font-size: var(--font-size-sm); color: var(--color-text-primary); text-align: center; white-space: nowrap; flex-shrink: 0; }
.col-ls { width: 44px; color: var(--color-text-secondary); }
.col-ym { width: 50px; font-size: var(--font-size-xs); }
.col-zs { width: 56px; font-size: var(--font-size-sm); color: var(--color-accent-light); }
.col-ben { text-align: left; padding-left: var(--space-2); }
.col-line { display: flex; justify-content: center; align-items: center; }
.col-mark { font-size: var(--font-size-md); font-weight: bold; }
.col-zhi { text-align: left; padding-left: var(--space-2); }

/* yao line drawing */
.yao-line {
  display: inline-flex; align-items: center; justify-content: center;
  width: 64px; height: 14px;
}
.yao-line.yang {
  width: 64px; height: 0;
  border-top: 4px solid var(--color-text-primary);
  border-radius: 2px;
}
.yao-line.yin { gap: 6px; }
.yao-line .seg {
  width: 28px; height: 0;
  border-top: 4px solid var(--color-text-primary);
  border-radius: 2px;
}
.yao-line .gap { width: 0; }

.zhanduan-text { white-space: pre-wrap; line-height: var(--line-height); }
.tag-badge { padding: 1px 8px; color: #fff; border-radius: var(--radius-sm); font-size: var(--font-size-xs); margin-right: var(--space-1); }

.edit-input, .edit-textarea { background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-accent); border-radius: var(--radius-md); padding: var(--space-1) var(--space-2); width: 100%; font-family: var(--font-family); }
.edit-textarea { padding: var(--space-2); min-height: 120px; }

.tag-add-btn { position: relative; display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border: 1px dashed var(--color-border-subtle); border-radius: var(--radius-sm); cursor: pointer; color: var(--color-text-muted); font-size: 14px; margin-left: 4px; transition: border-color var(--transition-fast); }
.tag-add-btn:hover { border-color: var(--color-accent); color: var(--color-accent); }
.tag-add-btn:hover .btn-edit-tip { display: block; }

.tag-editor-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 5000; display: flex; align-items: center; justify-content: center; }
.tag-editor { background: var(--color-bg-secondary); border-radius: var(--radius-xl); width: 360px; max-height: 480px; overflow: hidden; box-shadow: var(--shadow-lg); }
.tag-editor-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-3); border-bottom: 1px solid var(--color-border-primary); }
.tag-editor-header span { font-weight: bold; }
.tag-editor-header button { background: none; border: none; color: var(--color-text-secondary); font-size: 20px; cursor: pointer; }
.tag-editor-body { padding: var(--space-2) var(--space-3); overflow-y: auto; max-height: 380px; }
.tag-row { padding: 6px 8px; cursor: pointer; border-radius: var(--radius-sm); color: var(--color-text-secondary); display: flex; align-items: center; gap: 6px; transition: background var(--transition-fast); }
.tag-row:hover { background: var(--color-bg-tertiary); }
.tag-row.selected { color: var(--color-accent-light); }
.tag-badge-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
</style>
