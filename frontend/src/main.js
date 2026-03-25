/**
 * 六爻卦例分析系统 - 前端入口
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import './style.css'

// 创建Vue应用
const app = createApp(App)

// 使用Pinia状态管理
app.use(createPinia())

// 使用Vue Router
app.use(router)

// 使用Element Plus
app.use(ElementPlus, {
  locale: zhCn
})

// 挂载应用
app.mount('#app')
