<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <!-- 导航栏 -->
      <NavBar />

      <!-- 主内容区 -->
      <main class="main-content">
        <router-view />
      </main>

      <!-- 页脚 -->
      <footer class="footer">
        <span>六爻卦例分析系统 v1.0.0</span>
      </footer>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import NavBar from './components/NavBar.vue'
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  height: 100%;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.main-content {
  flex: 1;
  padding: 0;
  overflow: auto;
}

.footer {
  padding: 15px 20px;
  text-align: center;
  color: #909399;
  font-size: 12px;
  background-color: #fff;
  border-top: 1px solid #ebeef5;
}
</style>
