<template>
  <div class="guali-input">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>卦例录入</span>
          <el-tag type="info">标准格式: 年;月.日,本卦,之卦,占问事由,占断</el-tag>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        label-position="right"
        @submit.prevent="handleSubmit"
      >
        <!-- 时间输入 -->
        <el-divider content-position="left">时间信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="公历年" prop="solar_year">
              <el-input-number
                v-model="formData.solar_year"
                :min="1900"
                :max="2100"
                :step="1"
                style="width: 100%"
                placeholder="请输入年份"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="公历月" prop="solar_month">
              <el-input-number
                v-model="formData.solar_month"
                :min="1"
                :max="12"
                :step="1"
                style="width: 100%"
                placeholder="请输入月份"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="公历日" prop="solar_day">
              <el-input-number
                v-model="formData.solar_day"
                :min="1"
                :max="31"
                :step="1"
                style="width: 100%"
                placeholder="请输入日期"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 卦象输入 -->
        <el-divider content-position="left">卦象信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="本卦" prop="ben_gua_name">
              <el-autocomplete
                v-model="formData.ben_gua_name"
                :fetch-suggestions="queryGuaNames"
                placeholder="请输入本卦名（如：乾为天）"
                clearable
                style="width: 100%"
                @select="handleGuaSelect"
              >
                <template #default="{ item }">
                  <span>{{ item.value }}</span>
                </template>
              </el-autocomplete>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="之卦" prop="zhi_gua_name">
              <el-autocomplete
                v-model="formData.zhi_gua_name"
                :fetch-suggestions="queryGuaNames"
                placeholder="请输入之卦名（可选，留空表示无动爻）"
                clearable
                style="width: 100%"
              >
                <template #default="{ item }">
                  <span>{{ item.value }}</span>
                </template>
              </el-autocomplete>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 文本信息 -->
        <el-divider content-position="left">文本信息</el-divider>

        <el-form-item label="占问事由" prop="zhan_wen">
          <el-input
            v-model="formData.zhan_wen"
            type="textarea"
            :rows="2"
            placeholder="请输入占问事由（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="占断" prop="zhan_duan">
          <el-input
            v-model="formData.zhan_duan"
            type="textarea"
            :rows="2"
            placeholder="请输入占断（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="图片路径" prop="image_path">
          <el-input
            v-model="formData.image_path"
            placeholder="请输入图片文件名（可选，如：test.jpg）"
          >
            <template #append>
              <el-button @click="showImageConfig">查看存储路径</el-button>
            </template>
          </el-input>
          <div v-if="imageConfig" class="image-path-hint">
            <el-text size="small" type="info">
              图片请存放到: {{ imageConfig.absolute_path }}
            </el-text>
          </div>
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-space>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              提交卦例
            </el-button>
            <el-button @click="handleReset">重置表单</el-button>
            <el-button @click="handleFillExample">填充示例</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 提交成功后的结果展示 -->
    <el-card v-if="submittedGuali" class="result-card">
      <template #header>
        <div class="card-header">
          <span>提交成功</span>
          <el-tag type="success">ID: {{ submittedGuali.id }}</el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="公历时间">
          {{ submittedGuali.solar_year }}年{{ submittedGuali.solar_month }}月{{ submittedGuali.solar_day }}日
        </el-descriptions-item>
        <el-descriptions-item label="年柱">
          {{ submittedGuali.ganzhi_year }}
        </el-descriptions-item>
        <el-descriptions-item label="月柱">
          {{ submittedGuali.ganzhi_month }}
        </el-descriptions-item>
        <el-descriptions-item label="日柱">
          {{ submittedGuali.ganzhi_day }}
        </el-descriptions-item>
        <el-descriptions-item label="旬空">
          {{ submittedGuali.xunkong }}
        </el-descriptions-item>
        <el-descriptions-item label="卦宫">
          {{ submittedGuali.gongwei }} - {{ submittedGuali.gongwei_index }}
        </el-descriptions-item>
        <el-descriptions-item label="本卦">
          {{ submittedGuali.ben_gua_name }}
        </el-descriptions-item>
        <el-descriptions-item label="之卦">
          {{ submittedGuali.zhi_gua_name || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="占问事由" :span="2">
          {{ submittedGuali.zhan_wen || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="占断" :span="2">
          {{ submittedGuali.zhan_duan || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-space class="mt-20">
        <el-button type="primary" @click="viewDetail(submittedGuali.id)">
          查看详情
        </el-button>
        <el-button @click="continueInput">继续录入</el-button>
      </el-space>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createGuali, getImageConfig } from '../api'

const router = useRouter()

// 表单引用
const formRef = ref(null)

// 图片配置
const imageConfig = ref(null)

// 提交状态
const submitting = ref(false)

// 已提交的卦例
const submittedGuali = ref(null)

// 表单数据
const formData = reactive({
  solar_year: new Date().getFullYear(),
  solar_month: new Date().getMonth() + 1,
  solar_day: new Date().getDate(),
  ben_gua_name: '',
  zhi_gua_name: '',
  zhan_wen: '',
  zhan_duan: '',
  image_path: ''
})

// 六十四卦名称列表
const guaNames = [
  '乾为天', '天风姤', '天山遁', '天地否', '风地观', '山地剥', '火地晋', '火天大有',
  '坎为水', '水泽节', '水雷屯', '水火既济', '泽火革', '雷火丰', '地火明夷', '地水师',
  '艮为山', '山火贲', '山天大畜', '山泽损', '火泽睽', '天泽履', '风泽中孚', '风山渐',
  '震为雷', '雷地豫', '雷水解', '雷风恒', '地风升', '水风井', '泽风大过', '泽雷随',
  '巽为风', '风天小畜', '风火家人', '风雷益', '天雷无妄', '火雷噬嗑', '山雷颐', '山风蛊',
  '离为火', '火山旅', '火风鼎', '火水未济', '山水蒙', '风水涣', '天水讼', '天火同人',
  '坤为地', '地雷复', '地泽临', '地天泰', '雷天大壮', '泽天夬', '水天需', '水地比',
  '兑为泽', '泽水困', '泽地萃', '泽山咸', '水山蹇', '地山谦', '雷山小过', '雷泽归妹'
]

// 查询卦名建议
function queryGuaNames(queryString, cb) {
  const results = queryString
    ? guaNames
        .filter(name => name.includes(queryString))
        .map(name => ({ value: name }))
    : guaNames.map(name => ({ value: name }))
  cb(results)
}

// 处理卦名选择
function handleGuaSelect(item) {
  console.log('Selected gua:', item.value)
}

// 验证卦名
function validateGuaName(rule, value, callback) {
  if (!value) {
    // 之卦可以为空
    if (rule.field === 'zhi_gua_name') {
      callback()
      return
    }
    callback(new Error('请输入卦名'))
  } else if (!guaNames.includes(value)) {
    callback(new Error('请输入有效的卦名'))
  } else {
    callback()
  }
}

// 表单验证规则
const rules = {
  solar_year: [
    { required: true, message: '请输入年份', trigger: 'blur' }
  ],
  solar_month: [
    { required: true, message: '请输入月份', trigger: 'blur' }
  ],
  solar_day: [
    { required: true, message: '请输入日期', trigger: 'blur' }
  ],
  ben_gua_name: [
    { required: true, validator: validateGuaName, trigger: 'blur' }
  ],
  zhi_gua_name: [
    { validator: validateGuaName, trigger: 'blur' }
  ],
  zhan_wen: [
    { max: 500, message: '占问事由不能超过500个字符', trigger: 'blur' }
  ],
  zhan_duan: [
    { max: 500, message: '占断不能超过500个字符', trigger: 'blur' }
  ]
}

// 提交表单
async function handleSubmit() {
  try {
    // 验证表单
    await formRef.value.validate()

    submitting.value = true

    // 准备提交数据
    const data = {
      solar_year: formData.solar_year,
      solar_month: formData.solar_month,
      solar_day: formData.solar_day,
      ben_gua_name: formData.ben_gua_name,
      zhi_gua_name: formData.zhi_gua_name || null,
      zhan_wen: formData.zhan_wen || null,
      zhan_duan: formData.zhan_duan || null,
      image_path: formData.image_path || null
    }

    // 调用API
    const result = await createGuali(data)

    ElMessage.success('卦例创建成功')
    submittedGuali.value = result

  } catch (error) {
    if (error !== false) {
      ElMessage.error('卦例创建失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
function handleReset() {
  ElMessageBox.confirm('确定要重置表单吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    formRef.value.resetFields()
    submittedGuali.value = null
    ElMessage.success('表单已重置')
  }).catch(() => {})
}

// 填充示例数据
function handleFillExample() {
  formData.solar_year = 2024
  formData.solar_month = 2
  formData.solar_day = 12
  formData.ben_gua_name = '山风蛊'
  formData.zhi_gua_name = '火地晋'
  formData.zhan_wen = '占问股票走势'
  formData.zhan_duan = '占断上涨'
  formData.image_path = ''
  ElMessage.success('已填充示例数据')
}

// 显示图片配置
function showImageConfig() {
  if (imageConfig.value) {
    ElMessageBox.alert(
      `请将图片存放到以下路径:\n${imageConfig.value.absolute_path}\n\n支持的格式: ${imageConfig.value.allowed_extensions.join(', ')}\n最大文件大小: ${(imageConfig.value.max_file_size / 1024 / 1024).toFixed(2)} MB`,
      '图片存储路径',
      {
        confirmButtonText: '确定',
        type: 'info'
      }
    )
  }
}

// 查看详情
function viewDetail(id) {
  router.push(`/detail/${id}`)
}

// 继续录入
function continueInput() {
  submittedGuali.value = null
  // 保留日期，清除其他
  formData.ben_gua_name = ''
  formData.zhi_gua_name = ''
  formData.zhan_wen = ''
  formData.zhan_duan = ''
  formData.image_path = ''
}

// 加载图片配置
async function loadImageConfig() {
  try {
    imageConfig.value = await getImageConfig()
  } catch (error) {
    console.error('加载图片配置失败:', error)
  }
}

// 页面加载
onMounted(() => {
  loadImageConfig()
})
</script>

<style scoped>
.guali-input {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-path-hint {
  margin-top: 5px;
}

.result-card {
  margin-top: 20px;
}

.mt-20 {
  margin-top: 20px;
}
</style>
