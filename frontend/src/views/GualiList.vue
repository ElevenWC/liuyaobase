<template>
  <div class="guali-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>卦例列表</span>
          <el-space>
            <el-date-picker
              v-model="selectedYear"
              type="year"
              placeholder="选择年份筛选"
              value-format="YYYY"
              @change="handleYearChange"
              clearable
            />
            <el-button type="primary" @click="fetchList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-space>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="gualiList"
        stripe
        @row-click="handleRowClick"
        style="cursor: pointer"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="公历时间" width="120">
          <template #default="{ row }">
            {{ row.solar_year }}-{{ row.solar_month }}-{{ row.solar_day }}
          </template>
        </el-table-column>
        <el-table-column prop="ganzhi_day" label="日柱" width="80" />
        <el-table-column prop="ben_gua_name" label="本卦" width="100" />
        <el-table-column prop="zhi_gua_name" label="之卦" width="100">
          <template #default="{ row }">
            {{ row.zhi_gua_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="gongwei" label="卦宫" width="80" />
        <el-table-column prop="gongwei_index" label="宫位" width="80" />
        <el-table-column prop="zhan_wen" label="占问事由" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="viewDetail(row.id)">
              详情
            </el-button>
            <el-button type="danger" link @click.stop="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchList"
        @current-change="fetchList"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getGualiList, deleteGuali } from '../api'

const router = useRouter()

const loading = ref(false)
const gualiList = ref([])
const total = ref(0)
const selectedYear = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 获取列表
async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (selectedYear.value) {
      params.year = parseInt(selectedYear.value)
    }
    const result = await getGualiList(params)
    gualiList.value = result.items
    total.value = result.total
  } catch (error) {
    ElMessage.error('获取列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 年份变化
function handleYearChange() {
  pagination.page = 1
  fetchList()
}

// 行点击
function handleRowClick(row) {
  viewDetail(row.id)
}

// 查看详情
function viewDetail(id) {
  router.push(`/detail/${id}`)
}

// 删除
async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个卦例吗？删除后无法恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteGuali(id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.guali-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
