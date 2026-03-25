<template>
  <div class="field-library">
    <el-collapse v-model="activeCategories">
      <!-- 时间类字段 -->
      <el-collapse-item title="时间类" name="time">
        <div class="field-list">
          <el-tag
            v-for="field in timeFields"
            :key="field.key"
            class="field-tag"
            :type="field.type"
            draggable="true"
            @dragstart="handleDragStart($event, field)"
          >
            {{ field.label }}
            <span class="field-hint">{{ field.inputType === 'select' ? '下拉' : '输入' }}</span>
          </el-tag>
        </div>
      </el-collapse-item>

      <!-- 卦类字段 -->
      <el-collapse-item title="卦类" name="gua">
        <div class="field-list">
          <el-tag
            v-for="field in guaFields"
            :key="field.key"
            class="field-tag"
            :type="field.type"
            draggable="true"
            @dragstart="handleDragStart($event, field)"
          >
            {{ field.label }}
            <span class="field-hint">{{ field.inputType === 'select' ? '下拉' : '输入' }}</span>
          </el-tag>
        </div>
      </el-collapse-item>

      <!-- 爻类字段 -->
      <el-collapse-item title="爻类" name="yao">
        <div class="field-list">
          <el-tag
            v-for="field in yaoFields"
            :key="field.key"
            class="field-tag"
            :type="field.type"
            draggable="true"
            @dragstart="handleDragStart($event, field)"
          >
            {{ field.label }}
            <span class="field-hint">{{ field.inputType === 'select' ? '下拉' : '输入' }}</span>
          </el-tag>
        </div>
      </el-collapse-item>

      <!-- 关系类字段 -->
      <el-collapse-item title="关系类" name="relation">
        <div class="field-list">
          <el-tag
            v-for="field in relationFields"
            :key="field.key"
            class="field-tag"
            :type="field.type"
            draggable="true"
            @dragstart="handleDragStart($event, field)"
          >
            {{ field.label }}
            <span class="field-hint">关系</span>
          </el-tag>
        </div>
      </el-collapse-item>

      <!-- 神煞类字段 -->
      <el-collapse-item title="神煞类" name="shensha">
        <div class="field-list">
          <el-tag
            v-for="field in shenshaFields"
            :key="field.key"
            class="field-tag"
            :type="field.type"
            draggable="true"
            @dragstart="handleDragStart($event, field)"
          >
            {{ field.label }}
            <span class="field-hint">是/带</span>
          </el-tag>
        </div>
      </el-collapse-item>

      <!-- 其他字段 -->
      <el-collapse-item title="其他" name="other">
        <div class="field-list">
          <el-tag
            v-for="field in otherFields"
            :key="field.key"
            class="field-tag"
            :type="field.type"
            draggable="true"
            @dragstart="handleDragStart($event, field)"
          >
            {{ field.label }}
            <span class="field-hint">输入</span>
          </el-tag>
        </div>
      </el-collapse-item>

      <!-- 复合字段 -->
      <el-collapse-item title="复合字段 (使用.运算符)" name="compound">
        <div class="field-list">
          <el-tag
            v-for="field in compoundFields"
            :key="field.key"
            class="field-tag compound"
            type="warning"
            draggable="true"
            @dragstart="handleDragStart($event, field)"
          >
            {{ field.label }}
          </el-tag>
        </div>
        <el-alert
          type="info"
          :closable="false"
          class="hint-alert"
        >
          <template #title>
            <span class="hint-title">复合字段说明</span>
          </template>
          复合字段使用"."运算符访问特定爻位的属性，如"世爻.六亲"表示世爻的六亲属性
        </el-alert>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['field-drag'])

const activeCategories = ref(['time', 'gua', 'yao'])

// 时间类字段
const timeFields = ref([
  { key: 'solar_year', label: '公历年', category: 'time', inputType: 'input', valueType: 'number', type: '' },
  { key: 'solar_month_day', label: '公历月日', category: 'time', inputType: 'input', valueType: 'string', type: '' },
  { key: 'ganzhi_year', label: '年柱', category: 'time', inputType: 'select', options: getGanzhiOptions(), type: '' },
  { key: 'ganzhi_month', label: '月柱', category: 'time', inputType: 'select', options: getGanzhiOptions(), type: '' },
  { key: 'ganzhi_day', label: '日柱', category: 'time', inputType: 'select', options: getGanzhiOptions(), type: '' },
  { key: 'day_tiangan', label: '日干', category: 'time', inputType: 'select', options: getTianganOptions(), type: '' },
  { key: 'day_dizhi', label: '日支', category: 'time', inputType: 'select', options: getDizhiOptions(), type: '' },
  { key: 'xunkong', label: '旬空', category: 'time', inputType: 'select', options: getXunkongOptions(), type: '' }
])

// 卦类字段
const guaFields = ref([
  { key: 'ben_gua_name', label: '本卦名', category: 'gua', inputType: 'input', valueType: 'string', type: 'success' },
  { key: 'zhi_gua_name', label: '之卦名', category: 'gua', inputType: 'input', valueType: 'string', type: 'success' },
  { key: 'neigua', label: '内卦', category: 'gua', inputType: 'select', options: getDanGuaOptions(), type: 'success' },
  { key: 'waigua', label: '外卦', category: 'gua', inputType: 'select', options: getDanGuaOptions(), type: 'success' },
  { key: 'gongwei', label: '卦宫', category: 'gua', inputType: 'select', options: getGongweiOptions(), type: 'success' },
  { key: 'gongwei_index', label: '宫位', category: 'gua', inputType: 'select', options: getGongweiIndexOptions(), type: 'success' },
  { key: 'special_type', label: '特殊类型', category: 'gua', inputType: 'select', options: [
    { value: 'liuchong', label: '六冲卦' },
    { value: 'liuhe', label: '六合卦' },
    { value: 'none', label: '无' }
  ], type: 'success' }
])

// 爻类字段
const yaoFields = ref([
  { key: 'yao_position', label: '爻位', category: 'yao', inputType: 'select', options: getYaoPositionOptions(), type: 'primary' },
  { key: 'yao_type', label: '爻类型', category: 'yao', inputType: 'select', options: [
    { value: 1, label: '阳爻' },
    { value: 0, label: '阴爻' }
  ], type: 'primary' },
  { key: 'yao_state', label: '爻状态', category: 'yao', inputType: 'select', options: [
    { value: 1, label: '动爻' },
    { value: 0, label: '静爻' }
  ], type: 'primary' },
  { key: 'liuqin', label: '六亲', category: 'yao', inputType: 'select', options: getLiuqinOptions(), type: 'primary' },
  { key: 'liushen', label: '六神', category: 'yao', inputType: 'select', options: getLiushenOptions(), type: 'primary' },
  { key: 'dizhi', label: '地支', category: 'yao', inputType: 'select', options: getDizhiOptions(), type: 'primary' },
  { key: 'yao_wuxing', label: '爻地支五行', category: 'yao', inputType: 'select', options: getWuxingOptions(), type: 'primary' },
  { key: 'andong', label: '暗动', category: 'yao', inputType: 'select', options: [
    { value: 1, label: '有暗动' },
    { value: 0, label: '无暗动' }
  ], type: 'primary' },
  { key: 'shi_ying', label: '世应', category: 'yao', inputType: 'select', options: [
    { value: 'world', label: '世爻' },
    { value: 'response', label: '应爻' }
  ], type: 'primary' }
])

// 关系类字段
const relationFields = ref([
  { key: 'dizhi_he', label: '地支相合', category: 'relation', inputType: 'relation', relationType: 'he', type: 'warning' },
  { key: 'dizhi_chong', label: '地支相冲', category: 'relation', inputType: 'relation', relationType: 'chong', type: 'warning' },
  { key: 'dizhi_he_target', label: '地支相合地支', category: 'relation', inputType: 'relation', relationType: 'he_target', type: 'warning' },
  { key: 'dizhi_chong_target', label: '地支相冲地支', category: 'relation', inputType: 'relation', relationType: 'chong_target', type: 'warning' },
  { key: 'sanheju', label: '三合局', category: 'relation', inputType: 'select', options: [
    { value: 'shui', label: '申子辰(水)' },
    { value: 'mu', label: '亥卯未(木)' },
    { value: 'huo', label: '寅午戌(火)' },
    { value: 'jin', label: '巳酉丑(金)' }
  ], type: 'warning' },
  { key: 'wuxing_sheng', label: '五行相生', category: 'relation', inputType: 'relation', relationType: 'sheng', type: 'warning' },
  { key: 'wuxing_ke', label: '五行相克', category: 'relation', inputType: 'relation', relationType: 'ke', type: 'warning' },
  { key: 'shengwang_mujue', label: '生旺墓绝', category: 'relation', inputType: 'select', options: [
    { value: 'changsheng', label: '长生' },
    { value: 'diwang', label: '帝旺' },
    { value: 'mu', label: '墓' },
    { value: 'jue', label: '绝' }
  ], type: 'warning' },
  { key: 'fanyin_fuyin', label: '反吟伏吟', category: 'relation', inputType: 'select', options: [
    { value: 'yimao_fanyin', label: '易冒反吟' },
    { value: 'yaobian_fanyin', label: '爻变反吟' },
    { value: 'fuyin', label: '伏吟' }
  ], type: 'warning' },
  { key: 'fushen_feishen', label: '伏神飞神', category: 'relation', inputType: 'select', options: [
    { value: 'has_fushen', label: '有伏神' },
    { value: 'fu_ke_fei', label: '伏克飞' },
    { value: 'fei_ke_fu', label: '飞克伏' },
    { value: 'fu_sheng_fei', label: '伏生飞' },
    { value: 'fei_sheng_fu', label: '飞生伏' }
  ], type: 'warning' }
])

// 神煞类字段
const shenshaFields = ref([
  { key: 'ganlu', label: '干禄', category: 'shensha', inputType: 'select', options: [
    { value: 'is', label: '是干禄' },
    { value: 'dai', label: '带干禄' }
  ], type: 'danger' },
  { key: 'yima', label: '驿马', category: 'shensha', inputType: 'select', options: [
    { value: 'is', label: '是驿马' },
    { value: 'dai', label: '带驿马' }
  ], type: 'danger' },
  { key: 'yangren', label: '羊刃', category: 'shensha', inputType: 'select', options: [
    { value: 'is', label: '是羊刃' },
    { value: 'dai', label: '带羊刃' }
  ], type: 'danger' },
  { key: 'taohua', label: '桃花', category: 'shensha', inputType: 'select', options: [
    { value: 'is', label: '是桃花' },
    { value: 'dai', label: '带桃花' }
  ], type: 'danger' }
])

// 其他字段
const otherFields = ref([
  { key: 'zhan_wen', label: '占问事由', category: 'other', inputType: 'input', valueType: 'string', type: 'info' },
  { key: 'zhan_duan', label: '占断', category: 'other', inputType: 'input', valueType: 'string', type: 'info' },
  { key: 'yanqing_status', label: '占验情况', category: 'other', inputType: 'select', options: [
    { value: '应验', label: '应验' },
    { value: '模糊', label: '模糊' },
    { value: '不验', label: '不验' }
  ], type: 'info' }
])

// 复合字段
const compoundFields = ref([
  { key: 'world_yao.liuqin', label: '世爻.六亲', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'world_yao.dizhi', label: '世爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'world_yao.liushen', label: '世爻.六神', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'world_yao.wuxing', label: '世爻.五行', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'response_yao.liuqin', label: '应爻.六亲', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'response_yao.dizhi', label: '应爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'response_yao.liushen', label: '应爻.六神', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'response_yao.wuxing', label: '应爻.五行', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'moving_yao.liuqin', label: '动爻.六亲', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'moving_yao.dizhi', label: '动爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'qicai_yao.dizhi', label: '妻财爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'zisun_yao.dizhi', label: '子孙爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'guangui_yao.dizhi', label: '官鬼爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'fumu_yao.dizhi', label: '父母爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'xiongdi_yao.dizhi', label: '兄弟爻.地支', category: 'compound', inputType: 'compound', type: 'warning' },
  { key: 'day_dizhi.wuxing', label: '日支.五行', category: 'compound', inputType: 'compound', type: 'warning' }
])

// 辅助函数生成选项
function getTianganOptions() {
  const tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
  return tiangan.map(t => ({ value: t, label: t }))
}

function getDizhiOptions() {
  const dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
  return dizhi.map(d => ({ value: d, label: d }))
}

function getGanzhiOptions() {
  const tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
  const dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
  const result = []
  for (let i = 0; i < 60; i++) {
    result.push({ value: tiangan[i % 10] + dizhi[i % 12], label: tiangan[i % 10] + dizhi[i % 12] })
  }
  return result
}

function getXunkongOptions() {
  const xunkong = ['戌亥', '申酉', '午未', '辰巳', '寅卯', '子丑']
  return xunkong.map(x => ({ value: x, label: x }))
}

function getDanGuaOptions() {
  return [
    { value: '乾', label: '乾' },
    { value: '兑', label: '兑' },
    { value: '离', label: '离' },
    { value: '震', label: '震' },
    { value: '巽', label: '巽' },
    { value: '坎', label: '坎' },
    { value: '艮', label: '艮' },
    { value: '坤', label: '坤' }
  ]
}

function getGongweiOptions() {
  return ['乾宫', '坎宫', '艮宫', '震宫', '巽宫', '离宫', '坤宫', '兑宫'].map(g => ({ value: g, label: g }))
}

function getGongweiIndexOptions() {
  return ['本宫', '一世', '二世', '三世', '四世', '五世', '游魂', '归魂'].map(g => ({ value: g, label: g }))
}

function getYaoPositionOptions() {
  return ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'].map((y, i) => ({ value: i + 1, label: y }))
}

function getLiuqinOptions() {
  return ['父母', '官鬼', '子孙', '妻财', '兄弟'].map(l => ({ value: l, label: l }))
}

function getLiushenOptions() {
  return ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武'].map(l => ({ value: l, label: l }))
}

function getWuxingOptions() {
  return ['金', '木', '水', '火', '土'].map(w => ({ value: w, label: w }))
}

// 拖拽处理
function handleDragStart(event, field) {
  event.dataTransfer.setData('field', JSON.stringify(field))
  emit('field-drag', field)
}
</script>

<style scoped>
.field-library {
  height: 100%;
  overflow-y: auto;
}

.field-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.field-tag {
  cursor: grab;
  display: flex;
  align-items: center;
  gap: 4px;
}

.field-tag:active {
  cursor: grabbing;
}

.field-hint {
  font-size: 10px;
  opacity: 0.7;
  background: rgba(0, 0, 0, 0.1);
  padding: 1px 4px;
  border-radius: 3px;
}

.field-tag.compound {
  font-size: 12px;
}

.hint-alert {
  margin-top: 10px;
}

.hint-title {
  font-weight: bold;
}
</style>
