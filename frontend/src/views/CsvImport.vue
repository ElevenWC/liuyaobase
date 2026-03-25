<template>
  <div class="csv-import">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>CSV批量导入</span>
        </div>
      </template>

      <el-alert
        title="CSV格式说明"
        type="info"
        :closable="false"
        class="mb-20"
      >
        <p>CSV格式：年;月.日,本卦,之卦,占问事由,占断,图片路径</p>
        <p>示例：2024;02.12,山风蛊,火地晋,占问股票走势,占断上涨,</p>
        <p>注意：之卦、占问事由、占断、图片路径可为空</p>
      </el-alert>

      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".csv"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将CSV文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传CSV文件，支持UTF-8和GBK编码
          </div>
        </template>
      </el-upload>

      <el-space class="mt-20">
        <el-button type="primary" @click="handleImport" :loading="importing" :disabled="!selectedFile">
          开始导入
        </el-button>
        <el-button @click="handleClear">清空</el-button>
      </el-space>
    </el-card>

    <!-- 导入结果 -->
    <el-card v-if="importResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>导入结果</span>
          <el-tag :type="importResult.failed_count === 0 ? 'success' : 'warning'">
            成功: {{ importResult.success_count }} / 失败: {{ importResult.failed_count }}
          </el-tag>
        </div>
      </template>

      <el-progress
        :percentage="(importResult.success_count / importResult.total_rows * 100).toFixed(0)"
        :status="importResult.failed_count === 0 ? 'success' : 'warning'"
        class="mb-20"
      />

      <el-table :data="importResult.results" stripe max-height="400">
        <el-table-column prop="row_number" label="行号" width="80" />
        <el-table-column prop="success" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="guali_id" label="卦例ID" width="100">
          <template #default="{ row }">
            <el-link v-if="row.guali_id" type="primary" @click="viewDetail(row.guali_id)">
              {{ row.guali_id }}
            </el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="error" label="错误信息">
          <template #default="{ row }">
            <el-text v-if="row.error" type="danger">{{ row.error }}</el-text>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="importResult.errors.length > 0" class="error-list">
        <el-divider>错误详情</el-divider>
        <el-alert
          v-for="(error, index) in importResult.errors"
          :key="index"
          :title="error"
          type="error"
          :closable="false"
          class="mb-10"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { importCsv } from '../api'

const router = useRouter()

const uploadRef = ref(null)
const selectedFile = ref(null)
const importing = ref(false)
const importResult = ref(null)

// 文件选择
function handleFileChange(file) {
  selectedFile.value = file.raw
}

// 超出文件数量限制
function handleExceed() {
  ElMessage.warning('只能上传一个CSV文件')
}

// 开始导入
async function handleImport() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择CSV文件')
    return
  }

  importing.value = true
  importResult.value = null

  try {
    const result = await importCsv(selectedFile.value)
    importResult.value = result

    if (result.success_count > 0) {
      ElMessage.success(`成功导入 ${result.success_count} 条卦例`)
    }
    if (result.failed_count > 0) {
      ElMessage.warning(`${result.failed_count} 条导入失败`)
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    importing.value = false
  }
}

// 清空
function handleClear() {
  selectedFile.value = null
  importResult.value = null
  uploadRef.value?.clearFiles()
}

// 查看详情
function viewDetail(id) {
  router.push(`/detail/${id}`)
}
</script>

<style scoped>
.csv-import {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-area {
  width: 100%;
}

.mb-10 {
  margin-bottom: 10px;
}

.mb-20 {
  margin-bottom: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.result-card {
  margin-top: 20px;
}

.error-list {
  margin-top: 20px;
}
</style>
