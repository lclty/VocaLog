<template>
  <el-dialog :model-value="visible" title="导出 Staff 名单" width="500px" @close="$emit('update:visible', false)">
    <el-input type="textarea" :rows="15" v-model="text" readonly></el-input>
    <template #footer>
      <el-button type="primary" @click="copy">复制到剪贴板</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { sortRoles } from '../utils/constants' // 复用排序逻辑
import { ElMessage } from 'element-plus'

const props = defineProps(['visible', 'project'])
const emit = defineEmits(['update:visible'])
const text = ref('')

watch(() => props.visible, (val) => {
    if (val && props.project && props.project.staff) {
        const staffMap = props.project.staff
        // 1. 获取所有有人的工种
        const activeRoles = Object.keys(staffMap).filter(r => staffMap[r] && staffMap[r].length > 0)
        
        // 2. 排序
        const sorted = sortRoles(activeRoles)
        
        // 3. 生成文本
        const lines = sorted.map(role => {
            const people = staffMap[role].join('，')
            // 这里直接显示完整 Role 名，例如 "调教 (洛天依...)"
            return `${role}：${people}`
        })
        
        text.value = lines.join('\n')
    }
})

const copy = () => {
    navigator.clipboard.writeText(text.value)
    ElMessage.success('已复制')
    emit('update:visible', false)
}
</script>