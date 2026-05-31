<script setup>
import { ref, onMounted } from 'vue'
import { fetchTagTree, createTag, updateTag, deleteTag, reorderTags } from '../api/index.js'

const tree = ref([])
const newName = ref('')
const newParentId = ref(null)
const editId = ref(null)
const editName = ref('')
const error = ref('')

async function load() {
  try { const r = await fetchTagTree(); tree.value = r.data.data || [] }
  catch { error.value = '加载标签失败' }
}

onMounted(load)

async function addTag() {
  if (!newName.value.trim()) return
  try {
    await createTag({ name: newName.value.trim(), parent_id: newParentId.value })
    newName.value = ''; newParentId.value = null; await load()
  } catch (e) { error.value = '创建失败' }
}

function startEdit(tag) { editId.value = tag.id; editName.value = tag.name }
async function saveEdit(tag) {
  try { await updateTag(tag.id, { name: editName.value }); editId.value = null; await load() }
  catch { error.value = '重命名失败' }
}

async function removeTag(tag) {
  if (!confirm('删除标签 "' + tag.name + '"？')) return
  try { await deleteTag(tag.id); await load() }
  catch (e) { error.value = e.response?.data?.message || '删除失败' }
}

// ── 拖拽排序 ──
const dragId = ref(null)
function onDragStart(tag) { if (tag.depth === 0) dragId.value = tag.id }
async function onDrop(target) {
  if (dragId.value == null || target.depth !== 0 || dragId.value === target.id) return
  const ids = flatNodes().filter(n => n.depth === 0).map(n => n.id)
  const from = ids.indexOf(dragId.value)
  const to = ids.indexOf(target.id)
  if (from < 0 || to < 0) return
  ids.splice(from, 1)
  ids.splice(to, 0, dragId.value)
  try { await reorderTags(ids); await load() } catch { /* ok */ }
  dragId.value = null
}

const collapsed = ref({})

function toggleCollapse(node) {
  collapsed.value[node.id] = !collapsed.value[node.id]
}

const flatNodes = () => {
  const result = []
  function walk(nodes, depth) {
    for (const n of nodes) {
      result.push({ ...n, depth, hasChildren: !!(n.children && n.children.length) })
      if (n.children && n.children.length && collapsed.value[n.id]) {
        walk(n.children, depth + 1)
      }
    }
  }
  walk(tree.value, 0)
  return result
}
</script>

<template>
  <div class="tag-manager">
    <h2>标签管理</h2>
    <p v-if="error" class="error">{{ error }}</p>

    <div class="add-form">
      <input v-model="newName" placeholder="新标签名" @keyup.enter="addTag" />
      <select v-model="newParentId">
        <option :value="null">-- 一级标签 --</option>
        <option v-for="n in tree" :key="n.id" :value="n.id">{{ n.name }}</option>
      </select>
      <button @click="addTag" class="btn-add">创建</button>
    </div>

    <div class="tag-list">
      <div v-for="n in flatNodes()" :key="n.id" class="tag-item" :style="{ paddingLeft: (n.depth * 20 + 8) + 'px' }"
        :draggable="n.depth === 0"
        :class="{ 'drag-over': dragId && dragId !== n.id && n.depth === 0, 'drag-src': dragId === n.id }"
        @dragstart="onDragStart(n)"
        @dragover.prevent="n.depth === 0 && dragId !== n.id"
        @drop.prevent="onDrop(n)"
        @dragend="dragId = null">
        <template v-if="editId === n.id">
          <input v-model="editName" @keyup.enter="saveEdit(n)" @blur="saveEdit(n)" autofocus />
        </template>
        <template v-else>
          <span class="tag-name" :class="{ 'sys-tag': n.is_system, 'has-kids': n.hasChildren }"
            @click="n.hasChildren && toggleCollapse(n)"
            @dblclick="!n.is_system && !n.hasChildren && startEdit(n)">{{ n.hasChildren ? (collapsed[n.id] ? '▸' : '▾') + ' ' : '' }}{{ n.name }}</span>
          <span class="tag-children-count" v-if="n.children?.length">({{ n.children.length }} 子标签)</span>
          <span v-if="n.is_system" class="sys-badge">系统</span>
          <template v-if="!n.is_system">
            <button class="btn-sm" @click="startEdit(n)">重命名</button>
            <button class="btn-sm btn-del" @click="removeTag(n)">删除</button>
          </template>
        </template>
      </div>
      <p v-if="!tree.length" class="hint">暂无标签</p>
    </div>
  </div>
</template>

<style scoped>
.tag-manager { max-width: 600px; margin: var(--space-5) auto; color: var(--color-text-primary); padding: var(--space-4); }
h2 { margin-bottom: var(--space-4); }
.error { color: var(--color-danger); }
.add-form { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); }
.add-form input, .add-form select { padding: var(--space-2); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); background: var(--color-bg-input); color: var(--color-text-primary); }
.add-form input { flex: 1; }
.btn-add { padding: var(--space-2) var(--space-4); background: var(--color-accent-gradient); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; }
.tag-item { display: flex; align-items: center; gap: var(--space-2); padding: 6px 8px; border-radius: var(--radius-sm); }
.tag-item:hover { background: var(--color-bg-tertiary); }
.tag-name { flex: 1; cursor: pointer; }
.tag-name.has-kids { user-select: none; }
.tag-children-count { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.btn-sm { padding: 2px 10px; border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); background: var(--color-bg-secondary); color: var(--color-text-secondary); cursor: pointer; font-size: var(--font-size-xs); }
.btn-sm.btn-del { color: var(--color-danger); border-color: var(--color-danger); }
.hint { color: var(--color-text-muted); padding: var(--space-4); }
.sys-tag { color: var(--color-text-muted); cursor: default; }
.sys-badge { font-size: 10px; padding: 0 4px; background: var(--color-bg-tertiary); color: var(--color-text-muted); border-radius: var(--radius-sm); border: 1px solid var(--color-border-subtle); }
.tag-item[draggable="true"] { cursor: grab; }
.tag-item.drag-src { opacity: 0.4; }
.tag-item.drag-over { border-top: 2px solid var(--color-accent); }
</style>
