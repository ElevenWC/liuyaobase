<template>
  <div class="guali-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>卦例详情</span>
          <el-space>
            <el-button @click="goBack">返回列表</el-button>
            <el-button type="primary" @click="editGuali">编辑</el-button>
          </el-space>
        </div>
      </template>

      <template v-if="guali">
        <!-- 按照规范的输出格式展示 -->
        <div class="guali-display">
          <!-- 占问占断 -->
          <div class="display-row">
            <span class="label">占问：</span>
            <span class="value">{{ guali.zhan_wen || '无' }}</span>
          </div>
          <div class="display-row">
            <span class="label">占断：</span>
            <span class="value">{{ guali.zhan_duan || '无' }}</span>
          </div>

          <!-- 时间 -->
          <div class="display-row">
            <span class="label">时间：</span>
            <span class="value">{{ guali.solar_year }}年{{ guali.solar_month }}月{{ guali.solar_day }}日</span>
          </div>

          <!-- 神煞（按规范格式） -->
          <div class="display-row" v-if="guali.shensha">
            <span class="label">神煞：</span>
            <span class="value shensha-value">
              <span v-if="guali.shensha.ganlu">干禄-{{ guali.shensha.ganlu.dizhi }}</span>
              <span v-if="guali.shensha.yima">&nbsp;&nbsp;驿马-{{ guali.shensha.yima.dizhi }}</span>
              <span v-if="guali.shensha.yangren">&nbsp;&nbsp;羊刃-{{ guali.shensha.yangren.dizhi }}</span>
              <span v-if="guali.shensha.taohua">&nbsp;&nbsp;桃花-{{ guali.shensha.taohua.dizhi }}</span>
            </span>
          </div>

          <!-- 年柱月柱日柱旬空（表格形式） -->
          <div class="ganzhi-table">
            <table>
              <thead>
                <tr>
                  <th>年柱</th>
                  <th>月柱</th>
                  <th>日柱</th>
                  <th>旬空</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{{ guali.ganzhi_year }}</td>
                  <td>{{ guali.ganzhi_month }}</td>
                  <td>{{ guali.ganzhi_day }}</td>
                  <td>{{ guali.xunkong }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 图片 -->
          <div v-if="guali.image_path" class="image-section">
            <el-image
              :src="imageUrl"
              fit="contain"
              style="max-width: 600px; max-height: 400px"
              :preview-src-list="[imageUrl]"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                  <span>图片加载失败</span>
                </div>
              </template>
            </el-image>
          </div>
        </div>

        <!-- 分隔线 -->
        <el-divider>详细信息</el-divider>

        <!-- 占验情况 -->
        <YanqingAnnotation
          v-if="guali"
          :guali-id="guali.id"
          @updated="onYanqingUpdated"
        />

        <!-- 卦象基本信息 -->
        <el-descriptions title="卦象信息" :column="2" border class="section">
          <el-descriptions-item label="本卦">
            <el-tag type="primary">{{ guali.ben_gua_name }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="之卦">
            <el-tag v-if="guali.zhi_gua_name" type="success">{{ guali.zhi_gua_name }}</el-tag>
            <span v-else>无</span>
          </el-descriptions-item>
          <el-descriptions-item label="卦宫">{{ guali.gongwei }}</el-descriptions-item>
          <el-descriptions-item label="宫位">{{ guali.gongwei_index }}</el-descriptions-item>
          <el-descriptions-item label="本卦代码">{{ guali.ben_gua_code }}</el-descriptions-item>
          <el-descriptions-item label="之卦代码">{{ guali.zhi_gua_code || '-' }}</el-descriptions-item>
          <el-descriptions-item label="爻变代码">{{ guali.yao_bian_code }}</el-descriptions-item>
        </el-descriptions>

        <!-- 六爻详情（按规范从上爻到初爻排列） -->
        <div v-if="guali.yaos && guali.yaos.length > 0" class="section">
          <h3>六爻详情</h3>
          <el-table :data="reversedYaos" stripe border>
            <el-table-column label="爻位" width="100">
              <template #default="{ row }">
                {{ row.position_name || getPositionName(row.position) }}
                <el-tag v-if="row.is_world" type="warning" size="small">世</el-tag>
                <el-tag v-if="row.is_response" type="info" size="small">应</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="六神" width="80">
              <template #default="{ row }">
                {{ row.liushen || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="地支" width="80">
              <template #default="{ row }">
                {{ row.dizhi || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="六亲" width="80">
              <template #default="{ row }">
                {{ row.liuqin || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="类型" width="80">
              <template #default="{ row }">
                {{ row.yao_type === 1 ? '阳' : '阴' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.state === 1 ? 'danger' : 'info'" size="small">
                  {{ row.state === 1 ? '动' : '静' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 神煞详细信息 -->
        <div v-if="guali.shensha && hasShenshaDetails" class="section">
          <h3>神煞详情</h3>
          <el-table :data="shenshaTableData" stripe border>
            <el-table-column prop="name" label="神煞" width="100" />
            <el-table-column prop="dizhi" label="地支" width="80" />
            <el-table-column label="是否在卦中" width="120">
              <template #default="{ row }">
                <el-tag :type="row.isInGua ? 'success' : 'info'" size="small">
                  {{ row.isInGua ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="详细信息">
              <template #default="{ row }">
                <span v-if="row.yaos && row.yaos.length > 0">
                  <span v-for="(yao, idx) in row.yaos" :key="idx">
                    {{ getPositionName(yao.position) }}({{ yao.dizhi }}){{ yao.type }}
                    <span v-if="idx < row.yaos.length - 1">、</span>
                  </span>
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 伏神信息 -->
        <div v-if="guali.fushen && guali.fushen.has_fushen" class="section">
          <h3>伏神信息</h3>
          <el-table v-if="guali.fushen.fushen_list && guali.fushen.fushen_list.length > 0"
                    :data="guali.fushen.fushen_list" stripe border>
            <el-table-column prop="liuqin" label="六亲" width="100" />
            <el-table-column label="伏神爻位" width="100">
              <template #default="{ row }">
                {{ getPositionName(row.fushen_position) }}
              </template>
            </el-table-column>
            <el-table-column prop="fushen_dizhi" label="伏神地支" width="100" />
            <el-table-column prop="fushen_wuxing" label="伏神五行" width="100" />
            <el-table-column prop="feishen_dizhi" label="飞神地支" width="100" />
            <el-table-column prop="feishen_liuqin" label="飞神六亲" width="100" />
            <el-table-column prop="relation" label="伏飞关系" />
          </el-table>
          <el-empty v-else description="无伏神" :image-size="60" />
        </div>

        <!-- 反吟伏吟信息 -->
        <div v-if="guali.fanyin_fuyin && (guali.fanyin_fuyin.has_fanyin || guali.fanyin_fuyin.has_fuyin)" class="section">
          <h3>反吟伏吟</h3>
          <el-table v-if="guali.fanyin_fuyin.details && guali.fanyin_fuyin.details.length > 0"
                    :data="guali.fanyin_fuyin.details" stripe border>
            <el-table-column prop="position" label="位置" width="100" />
            <el-table-column prop="from" label="原卦" width="100" />
            <el-table-column prop="to" label="变卦" width="100" />
            <el-table-column prop="type" label="类型" />
          </el-table>
        </div>
      </template>

      <el-empty v-else-if="!loading" description="卦例不存在" />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑卦例" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="占问事由">
          <el-input v-model="editForm.zhan_wen" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="占断">
          <el-input v-model="editForm.zhan_duan" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="图片路径">
          <el-input v-model="editForm.image_path" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { getGualiDetail, updateGuali, getImageUrl } from '../api'
import YanqingAnnotation from '@/components/YanqingAnnotation.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const guali = ref(null)

// 编辑
const editDialogVisible = ref(false)
const saving = ref(false)
const editForm = reactive({
  zhan_wen: '',
  zhan_duan: '',
  image_path: ''
})

// 计算图片URL
const imageUrl = computed(() => {
  if (guali.value?.image_path) {
    return getImageUrl(guali.value.image_path)
  }
  return ''
})

// 反转爻列表（从上爻到初爻显示）
const reversedYaos = computed(() => {
  if (!guali.value?.yaos) return []
  return [...guali.value.yaos].reverse()
})

// 爻位名称映射
function getPositionName(position) {
  const names = { 1: '初爻', 2: '二爻', 3: '三爻', 4: '四爻', 5: '五爻', 6: '上爻' }
  return names[position] || `第${position}爻`
}

// 神煞表格数据
const shenshaTableData = computed(() => {
  if (!guali.value?.shensha) return []
  const shenshaNames = {
    'ganlu': '干禄',
    'yima': '驿马',
    'yangren': '羊刃',
    'taohua': '桃花'
  }
  const data = []
  for (const [key, name] of Object.entries(shenshaNames)) {
    const shenshaInfo = guali.value.shensha[key]
    if (shenshaInfo) {
      data.push({
        key: key,
        name: name,
        dizhi: shenshaInfo.dizhi,
        isInGua: shenshaInfo.is_in_gua,
        yaos: shenshaInfo.yaos || []
      })
    }
  }
  return data
})

// 是否有神煞详情
const hasShenshaDetails = computed(() => {
  if (!guali.value?.shensha) return false
  return guali.value.shensha.ganlu?.is_in_gua ||
         guali.value.shensha.yima?.is_in_gua ||
         guali.value.shensha.yangren?.is_in_gua ||
         guali.value.shensha.taohua?.is_in_gua
})

// 获取详情
async function fetchDetail() {
  loading.value = true
  try {
    const id = parseInt(route.params.id)
    guali.value = await getGualiDetail(id)
  } catch (error) {
    ElMessage.error('获取详情失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 返回列表
function goBack() {
  router.push('/list')
}

// 编辑
function editGuali() {
  if (guali.value) {
    editForm.zhan_wen = guali.value.zhan_wen || ''
    editForm.zhan_duan = guali.value.zhan_duan || ''
    editForm.image_path = guali.value.image_path || ''
    editDialogVisible.value = true
  }
}

// 保存编辑
async function saveEdit() {
  saving.value = true
  try {
    await updateGuali(guali.value.id, editForm)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    fetchDetail()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 格式化神煞
function formatShensha(value) {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}

// 占验情况更新回调
function onYanqingUpdated(data) {
  console.log('占验情况已更新:', data)
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.guali-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section {
  margin-bottom: 20px;
}

.section h3 {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
}

/* 按照规范格式的样式 */
.guali-display {
  background-color: #fafafa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.display-row {
  margin-bottom: 12px;
  font-size: 15px;
  line-height: 1.8;
}

.display-row .label {
  font-weight: bold;
  color: #303133;
  min-width: 60px;
  display: inline-block;
}

.display-row .value {
  color: #606266;
}

.display-row .shensha-value {
  font-family: 'Microsoft YaHei', sans-serif;
  letter-spacing: 1px;
}

/* 干支表格样式 */
.ganzhi-table {
  margin: 15px 0;
}

.ganzhi-table table {
  border-collapse: collapse;
  width: auto;
  min-width: 400px;
}

.ganzhi-table th,
.ganzhi-table td {
  border: 1px solid #dcdfe6;
  padding: 10px 20px;
  text-align: center;
  font-size: 14px;
}

.ganzhi-table th {
  background-color: #f5f7fa;
  font-weight: bold;
  color: #303133;
}

.ganzhi-table td {
  color: #606266;
}

/* 图片区域 */
.image-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  display: inline-block;
}
</style>
