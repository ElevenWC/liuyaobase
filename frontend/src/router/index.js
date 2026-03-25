/**
 * 六爻卦例分析系统 - 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/input',
    name: 'GualiInput',
    component: () => import('../views/GualiInput.vue'),
    meta: { title: '卦例录入' }
  },
  {
    path: '/csv-import',
    name: 'CsvImport',
    component: () => import('../views/CsvImport.vue'),
    meta: { title: 'CSV导入' }
  },
  {
    path: '/list',
    name: 'GualiList',
    component: () => import('../views/GualiList.vue'),
    meta: { title: '卦例列表' }
  },
  {
    path: '/detail/:id',
    name: 'GualiDetail',
    component: () => import('../views/GualiDetail.vue'),
    meta: { title: '卦例详情' },
    props: true
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
    meta: { title: '复杂检索' }
  },
  {
    path: '/image-config',
    name: 'ImageConfig',
    component: () => import('../views/ImageConfig.vue'),
    meta: { title: '图片配置' }
  },
  {
    path: '/stock',
    name: 'StockAnalysis',
    component: () => import('../views/StockAnalysis.vue'),
    meta: { title: '股票分析' }
  },
  {
    // 404页面
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 六爻卦例分析系统` : '六爻卦例分析系统'
  next()
})

export default router
