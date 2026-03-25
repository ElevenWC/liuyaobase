<template>
  <el-menu
    :default-active="activeIndex"
    class="nav-bar"
    mode="horizontal"
    :ellipsis="false"
    @select="handleSelect"
  >
    <!-- Logo -->
    <div class="logo">
      <span class="logo-text">六爻卦例分析系统</span>
    </div>

    <div class="flex-grow" />

    <!-- 导航菜单 -->
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>首页</span>
    </el-menu-item>

    <el-menu-item index="/input">
      <el-icon><Edit /></el-icon>
      <span>卦例录入</span>
    </el-menu-item>

    <el-menu-item index="/csv-import">
      <el-icon><Upload /></el-icon>
      <span>CSV导入</span>
    </el-menu-item>

    <el-menu-item index="/list">
      <el-icon><List /></el-icon>
      <span>卦例列表</span>
    </el-menu-item>

    <el-menu-item index="/search">
      <el-icon><Search /></el-icon>
      <span>复杂检索</span>
    </el-menu-item>

    <el-menu-item index="/stock">
      <el-icon><TrendCharts /></el-icon>
      <span>股票分析</span>
    </el-menu-item>

    <el-menu-item index="/image-config">
      <el-icon><Picture /></el-icon>
      <span>图片配置</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  HomeFilled,
  Edit,
  Upload,
  List,
  Search,
  Picture,
  TrendCharts
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 当前激活的菜单项
const activeIndex = computed(() => route.path)

// 处理菜单选择
function handleSelect(index) {
  router.push(index)
}
</script>

<style scoped>
.nav-bar {
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #545c64;
  border-bottom: none;
}

.nav-bar .el-menu-item {
  color: #fff;
  border-bottom: none;
}

.nav-bar .el-menu-item:hover {
  background-color: #434a50;
}

.nav-bar .el-menu-item.is-active {
  background-color: #409eff;
  border-bottom: none;
}

.logo {
  display: flex;
  align-items: center;
  padding: 0 20px;
  margin-right: 20px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  white-space: nowrap;
}

.flex-grow {
  flex-grow: 1;
}
</style>
