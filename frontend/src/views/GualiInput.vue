<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { importManual } from '../api/index.js'
import { fetchGualiList } from '../api/index.js'

const router = useRouter()

const form = ref({
  zhanwen_time: new Date().toISOString().slice(0, 16),
  zhanwen_shiyou: '',
  zhanduan: '',
  ben_name: '',
  zhi_name: '',
})

const guaList = ref([])
const submitting = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  try {
    const res = await fetchGualiList({ page: 1, page_size: 1 })
    // 从 bagong_gua 加载卦名列表——用 /api/guaci 不行，直接用 guali 列表请求触发后端已运行
  } catch { /* 列表可能空 */ }
  // 通过单独的请求加载 64 卦名
  try {
    const res2 = await fetch(import.meta.env.BASE_URL + 'api/guaci/111111')
    // 如果 guaci API 可用，说明后端在线
  } catch { /* ok */ }
  // 直接用静态的 64 卦名列表
  guaList.value = [
    '乾为天','坤为地','水雷屯','山水蒙','水天需','天水讼','地水师','水地比',
    '风天小畜','天泽履','地天泰','天地否','天火同人','火天大有','地山谦','雷地豫',
    '泽雷随','山风蛊','地泽临','风地观','火雷噬嗑','山火贲','山地剥','地雷复',
    '天雷无妄','山天大畜','山雷颐','泽风大过','坎为水','离为火','泽山咸','雷风恒',
    '天山遁','雷天大壮','火地晋','地火明夷','风火家人','火泽睽','水山蹇','雷水解',
    '山泽损','风雷益','泽天夬','天风姤','泽地萃','地风升','泽水困','水风井',
    '泽火革','火风鼎','震为雷','艮为山','风山渐','雷泽归妹','雷火丰','火山旅',
    '巽为风','兑为泽','风水涣','水泽节','风泽中孚','雷山小过','水火既济','火水未济',
  ]
})

async function submit() {
  if (!form.value.zhanwen_time || !form.value.zhanwen_shiyou || !form.value.ben_name) {
    errorMsg.value = '占问时间、占问事由、本卦名称为必填项'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    await importManual(form.value)
    router.push('/')
  } catch (e) {
    errorMsg.value = e.response?.data?.message || '导入失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="guali-input">
    <h2>手动导入卦例</h2>
    <form @submit.prevent="submit" class="input-form">
      <label>
        占问时间
        <input type="datetime-local" v-model="form.zhanwen_time" />
      </label>
      <label>
        占问事由 <span class="required">*</span>
        <input v-model="form.zhanwen_shiyou" placeholder="例：上证指数05.22走势" />
      </label>
      <label>
        占断内容
        <textarea v-model="form.zhanduan" rows="4" placeholder="可选" />
      </label>
      <label>
        本卦 <span class="required">*</span>
        <select v-model="form.ben_name">
          <option value="">-- 请选择 --</option>
          <option v-for="name in guaList" :key="name" :value="name">{{ name }}</option>
        </select>
      </label>
      <label>
        之卦
        <select v-model="form.zhi_name">
          <option value="">-- 无（静卦） --</option>
          <option v-for="name in guaList" :key="name" :value="name">{{ name }}</option>
        </select>
      </label>
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <button type="submit" :disabled="submitting">
        {{ submitting ? '提交中...' : '提交' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.guali-input { max-width: 500px; margin: 20px auto; }
.input-form { display: flex; flex-direction: column; gap: 12px; }
label { display: flex; flex-direction: column; gap: 4px; font-weight: 500; }
.required { color: red; }
input, textarea, select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.error { color: red; }
button { padding: 10px 24px; background: #409eff; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { opacity: 0.6; }
</style>
