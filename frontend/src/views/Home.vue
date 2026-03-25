<template>
  <div class="home">
    <el-row :gutter="20">
      <!-- 欢迎信息 -->
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <span>欢迎使用六爻卦例分析系统</span>
            </div>
          </template>
          <div class="welcome-content">
            <p>本系统是一个专业的六爻卦例管理与分析平台，提供以下功能：</p>
            <el-row :gutter="20" class="feature-list">
              <el-col :span="8" v-for="feature in features" :key="feature.title">
                <el-card shadow="hover" class="feature-card" @click="navigateTo(feature.path)">
                  <div class="feature-icon">
                    <el-icon :size="40"><component :is="feature.icon" /></el-icon>
                  </div>
                  <h3>{{ feature.title }}</h3>
                  <p>{{ feature.description }}</p>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态 -->
    <el-row :gutter="20" class="status-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-button type="primary" size="small" @click="checkHealth" :loading="checking">
                刷新
              </el-button>
            </div>
          </template>
          <div v-if="healthStatus" class="health-status">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="状态">
                <el-tag :type="healthStatus.status === 'ok' ? 'success' : 'danger'">
                  {{ healthStatus.status === 'ok' ? '正常' : '异常' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据库">
                <el-tag :type="healthStatus.database === 'connected' ? 'success' : 'danger'">
                  {{ healthStatus.database === 'connected' ? '已连接' : '未连接' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="版本">
                {{ healthStatus.version }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="点击刷新检查系统状态" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>图片存储配置</span>
              <el-button type="primary" size="small" @click="loadImageConfig" :loading="loadingConfig">
                刷新
              </el-button>
            </div>
          </template>
          <div v-if="imageConfig" class="image-config">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="存储路径">
                <el-tag>{{ imageConfig.storage_path }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="绝对路径">
                <el-text type="primary" size="small" class="copy-text" @click="copyPath">
                  {{ imageConfig.absolute_path }}
                  <el-icon><CopyDocument /></el-icon>
                </el-text>
              </el-descriptions-item>
              <el-descriptions-item label="支持格式">
                <el-tag v-for="ext in imageConfig.allowed_extensions" :key="ext" class="mr-5">
                  {{ ext }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="最大大小">
                {{ formatSize(imageConfig.max_file_size) }}
              </el-descriptions-item>
            </el-descriptions>
            <el-alert
              title="请将图片文件存放到上述路径"
              type="info"
              :closable="false"
              class="mt-10"
            />
          </div>
          <el-empty v-else description="点击刷新加载配置" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速入口 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <el-space wrap>
            <el-button type="primary" @click="navigateTo('/input')">
              <el-icon><Plus /></el-icon>
              新建卦例
            </el-button>
            <el-button @click="navigateTo('/csv-import')">
              <el-icon><Upload /></el-icon>
              CSV导入
            </el-button>
            <el-button @click="navigateTo('/list')">
              <el-icon><List /></el-icon>
              查看列表
            </el-button>
            <el-button @click="navigateTo('/search')">
              <el-icon><Search /></el-icon>
              复杂检索
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Upload,
  List,
  Search,
  Picture,
  Plus,
  CopyDocument
} from '@element-plus/icons-vue'
import { healthCheck, getImageConfig } from '../api'

const router = useRouter()

// 功能列表
const features = [
  {
    title: '卦例录入',
    description: '手动输入卦例信息，包括时间、本卦、之卦等',
    icon: Edit,
    path: '/input'
  },
  {
    title: 'CSV导入',
    description: '批量导入CSV格式的卦例数据',
    icon: Upload,
    path: '/csv-import'
  },
  {
    title: '卦例列表',
    description: '查看和管理所有已录入的卦例',
    icon: List,
    path: '/list'
  },
  {
    title: '复杂检索',
    description: '多条件组合检索卦例',
    icon: Search,
    path: '/search'
  },
  {
    title: '卦例详情',
    description: '查看卦例的完整卦理分析',
    icon: Picture,
    path: '/list'
  },
  {
    title: '图片配置',
    description: '查看图片存储路径配置',
    icon: Picture,
    path: '/image-config'
  }
]

// 系统状态
const healthStatus = ref(null)
const checking = ref(false)

// 图片配置
const imageConfig = ref(null)
const loadingConfig = ref(false)

// 检查系统状态
async function checkHealth() {
  checking.value = true
  try {
    healthStatus.value = await healthCheck()
    ElMessage.success('系统状态检查成功')
  } catch (error) {
    ElMessage.error('系统状态检查失败')
  } finally {
    checking.value = false
  }
}

// 加载图片配置
async function loadImageConfig() {
  loadingConfig.value = true
  try {
    imageConfig.value = await getImageConfig()
    ElMessage.success('图片配置加载成功')
  } catch (error) {
    ElMessage.error('图片配置加载失败')
  } finally {
    loadingConfig.value = false
  }
}

// 导航到指定页面
function navigateTo(path) {
  router.push(path)
}

// 格式化文件大小
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 复制路径
function copyPath() {
  if (imageConfig.value && navigator.clipboard) {
    navigator.clipboard.writeText(imageConfig.value.absolute_path)
    ElMessage.success('路径已复制到剪贴板')
  }
}

// 页面加载时检查状态
onMounted(() => {
  checkHealth()
  loadImageConfig()
})
</script>

<style scoped>
.home {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content {
  text-align: center;
}

.welcome-content > p {
  margin-bottom: 30px;
  color: #666;
}

.feature-list {
  margin-top: 20px;
}

.feature-card {
  cursor: pointer;
  text-align: center;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  margin-bottom: 15px;
  color: #409eff;
}

.feature-card h3 {
  margin: 10px 0;
  font-size: 16px;
}

.feature-card p {
  color: #999;
  font-size: 13px;
}

.status-section {
  margin-top: 20px;
}

.health-status,
.image-config {
  padding: 10px 0;
}

.copy-text {
  cursor: pointer;
}

.copy-text:hover {
  text-decoration: underline;
}

.mr-5 {
  margin-right: 5px;
}

.mt-10 {
  margin-top: 10px;
}

.quick-actions {
  margin-top: 20px;
}
</style>
