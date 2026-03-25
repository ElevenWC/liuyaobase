<template>
  <div class="image-config">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>图片存储配置</span>
          <el-button type="primary" @click="loadConfig">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <template v-if="config">
        <el-alert
          title="重要提示"
          type="warning"
          :closable="false"
          class="mb-20"
        >
          请将卦例图片存放到以下路径，系统将通过该路径访问图片。
        </el-alert>

        <el-descriptions :column="1" border>
          <el-descriptions-item label="配置路径">
            <el-tag>{{ config.storage_path }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="绝对路径">
            <div class="path-container">
              <el-text type="primary" size="large">{{ config.absolute_path }}</el-text>
              <el-button type="primary" size="small" @click="copyPath">
                <el-icon><CopyDocument /></el-icon>
                复制路径
              </el-button>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="支持格式">
            <el-space wrap>
              <el-tag v-for="ext in config.allowed_extensions" :key="ext" type="info">
                .{{ ext }}
              </el-tag>
            </el-space>
          </el-descriptions-item>
          <el-descriptions-item label="最大文件大小">
            <el-tag type="warning">{{ formatSize(config.max_file_size) }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h3>使用说明</h3>
        <el-steps direction="vertical" :active="3">
          <el-step title="复制存储路径">
            <template #description>
              点击上方"复制路径"按钮，复制图片存储的绝对路径
            </template>
          </el-step>
          <el-step title="存放图片">
            <template #description>
              将卦例图片复制到该路径下，建议使用有意义的文件名，如：20240212_股票占问.jpg
            </template>
          </el-step>
          <el-step title="录入卦例">
            <template #description>
              在卦例录入页面填写图片文件名（如：20240212_股票占问.jpg）
            </template>
          </el-step>
        </el-steps>

        <el-divider />

        <h3>已上传图片</h3>
        <el-table :data="imageList" stripe v-loading="loadingList">
          <el-table-column prop="filename" label="文件名" />
          <el-table-column label="URL" width="300">
            <template #default="{ row }">
              <el-link :href="row.url" target="_blank" type="primary">
                {{ row.url }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="modified" label="修改时间" width="180" />
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, CopyDocument } from '@element-plus/icons-vue'
import { getImageConfig, getImageList } from '../api'

const loading = ref(false)
const loadingList = ref(false)
const config = ref(null)
const imageList = ref([])

// 加载配置
async function loadConfig() {
  loading.value = true
  try {
    config.value = await getImageConfig()
    ElMessage.success('配置加载成功')
  } catch (error) {
    ElMessage.error('加载配置失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 加载图片列表
async function loadImageList() {
  loadingList.value = true
  try {
    const result = await getImageList()
    imageList.value = result.images || []
  } catch (error) {
    console.error('加载图片列表失败:', error)
  } finally {
    loadingList.value = false
  }
}

// 复制路径
function copyPath() {
  if (config.value && navigator.clipboard) {
    navigator.clipboard.writeText(config.value.absolute_path)
    ElMessage.success('路径已复制到剪贴板')
  }
}

// 格式化文件大小
function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

onMounted(() => {
  loadConfig()
  loadImageList()
})
</script>

<style scoped>
.image-config {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mb-20 {
  margin-bottom: 20px;
}

.path-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

h3 {
  margin-bottom: 15px;
}
</style>
