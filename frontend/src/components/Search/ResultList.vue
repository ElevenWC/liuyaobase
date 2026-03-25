<template>
  <div class="result-list">
    <div class="result-header">
      <span class="title">检索结果</span>
      <span class="count" v-if="total > 0">共 {{ total }} 条</span>
    </div>

    <el-divider />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在检索...</span>
    </div>

    <!-- 空状态 -->
    <el-empty v-else-if="results.length === 0" description="暂无检索结果" :image-size="80" />

    <!-- 结果列表 -->
    <div v-else class="results-container">
      <el-scrollbar height="calc(100vh - 320px)">
        <div
          v-for="item in results"
          :key="item.id"
          class="result-item"
          @click="$emit('view-detail', item.id)"
        >
          <div class="item-header">
            <el-tag type="primary" size="small">{{ item.ben_gua_name }}</el-tag>
            <el-tag v-if="item.zhi_gua_name" type="success" size="small">
              {{ item.zhi_gua_name }}
            </el-tag>
            <span class="item-id">#{{ item.id }}</span>
          </div>

          <div class="item-time">
            {{ item.solar_year }}年{{ item.solar_month }}月{{ item.solar_day }}日
            <el-divider direction="vertical" />
            {{ item.ganzhi_day }}
          </div>

          <div class="item-info">
            <span>{{ item.gongwei }} · {{ item.gongwei_index }}</span>
          </div>

          <div class="item-zhanwen" v-if="item.zhan_wen">
            占问：{{ item.zhan_wen }}
          </div>
        </div>
      </el-scrollbar>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          small
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 导出按钮 -->
    <div class="export-section" v-if="results.length > 0">
      <el-button type="primary" size="small" @click="$emit('export')">
        <el-icon><Download /></el-icon>
        导出结果
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Loading, Download } from '@element-plus/icons-vue'

const props = defineProps({
  results: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['page-change', 'view-detail', 'export'])

const currentPage = ref(1)
const pageSize = ref(20)

watch([currentPage, pageSize], ([page, size]) => {
  emit('page-change', page, size)
})

function handlePageChange(page) {
  currentPage.value = page
}

function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
}
</script>

<style scoped>
.result-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header .title {
  font-weight: bold;
  font-size: 14px;
}

.result-header .count {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--el-text-color-secondary);
  gap: 10px;
}

.loading-container .el-icon {
  font-size: 24px;
}

.results-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.result-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--el-bg-color);
}

.result-item:hover {
  border-color: var(--el-color-primary-light-3);
  background: var(--el-color-primary-light-9);
  transform: translateX(4px);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.item-id {
  margin-left: auto;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.item-time {
  font-size: 13px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
}

.item-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.item-zhanwen {
  font-size: 12px;
  color: var(--el-text-color-regular);
  background: var(--el-fill-color-light);
  padding: 6px 8px;
  border-radius: 4px;
  margin-top: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-container {
  padding: 10px 0;
  display: flex;
  justify-content: center;
}

.export-section {
  padding-top: 10px;
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: center;
}
</style>
