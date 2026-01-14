<template>
  <el-table :data="projects" style="width: 100%" border stripe>
    <el-table-column prop="title" label="工程名称" width="180">
        <template #default="scope">
            <span style="font-weight: bold; color: #303133;">{{ scope.row.title }}</span>
        </template>
    </el-table-column>
    
    <el-table-column label="虚拟歌手声库" min-width="280">
        <template #default="scope">
            <div v-if="scope.row.singer && scope.row.singer.length">
                <el-tag 
                    v-for="(s, i) in scope.row.singer" :key="i"
                    effect="plain"
                    style="margin-bottom: 4px; display: block; width: fit-content; max-width: 100%; white-space: normal; height: auto; padding: 5px;"
                >
                    {{ s }}
                </el-tag>
            </div>
            <span v-else style="color: #ccc;">未指定</span>
        </template>
    </el-table-column>
    
    <el-table-column label="进度追踪" min-width="450">
        <template #default="scope">
            <div class="progress-list">
                <div v-for="role in getSortedRoles(scope.row)" :key="role" class="progress-row-container">
                    
                    <div class="progress-row">
                        <div 
                            class="role-name" 
                            :class="{ 'role-all-done': isRoleAllDone(scope.row, role), 'clickable': isLongRole(role) }"
                            @click="toggleExpand(scope.row.id, role)"
                        >
                            <span v-if="isLongRole(role)">
                                {{ isExpanded(scope.row.id, role) ? '▼ ' + role : '▶ 调教 (点击展开)' }}
                            </span>
                            <span v-else>{{ role }}</span>
                        </div>
                        
                        <div class="staff-progress-group">
                            <el-tooltip 
                                v-for="staffName in scope.row.staff[role]" :key="staffName"
                                :content="getTooltip(scope.row, role, staffName)" 
                                placement="top"
                            >
                                <div 
                                    class="staff-step" 
                                    :class="{ done: isStaffDone(scope.row, role, staffName) }"
                                    @click="markStaffDone(scope.row, role, staffName)"
                                >
                                    {{ staffName }}
                                </div>
                            </el-tooltip>
                        </div>
                    </div>

                    <div v-if="isLongRole(role) && isExpanded(scope.row.id, role)" class="role-detail-info">
                        {{ role.replace('调教 ', '') }}
                    </div>

                </div>
                
                <div v-if="isProjectAllDone(scope.row)" style="margin-top:10px; color:#67C23A; font-weight:bold; font-size:13px; display:flex; align-items:center;">
                    <el-icon style="margin-right:4px"><Select /></el-icon> 项目已全部完成
                </div>
            </div>
        </template>
    </el-table-column>

    <el-table-column label="Staff名单" width="200">
        <template #default="scope">
            <div v-for="role in getSortedRoles(scope.row)" :key="role" style="font-size: 12px; margin-bottom: 2px;">
                <span style="font-weight: bold;">{{ getShortName(role) }}:</span> 
                {{ scope.row.staff[role].join(', ') }}
            </div>
        </template>
    </el-table-column>

    <el-table-column label="操作" width="100" fixed="right">
        <template #default="scope">
            <div class="action-column">
                <el-button class="action-btn" color="#626aef" plain @click="openFolder(scope.row.path)">打开目录</el-button>
                <el-button class="action-btn" type="primary" plain @click="$emit('edit', scope.row)">编辑工程</el-button>
                <el-button class="action-btn" type="success" plain @click="$emit('export', scope.row)">查看名单</el-button>
            </div>
        </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Select } from '@element-plus/icons-vue'
import { sortRoles } from '../utils/constants'

const props = defineProps(['projects'])
const emit = defineEmits(['refresh', 'edit', 'export'])

// 展开状态存储: { projectId_roleName: boolean }
const expandedStates = ref({})

// 获取并排序该项目有的工种
const getSortedRoles = (row) => {
    if (!row.staff) return []
    const activeRoles = Object.keys(row.staff).filter(role => row.staff[role] && row.staff[role].length > 0)
    return sortRoles(activeRoles)
}

const isStaffDone = (row, role, staffName) => {
    try { return !!(row.progress && row.progress[role] && row.progress[role][staffName]) } catch { return false }
}

const isRoleAllDone = (row, role) => {
    const staffList = row.staff[role] || []
    if (staffList.length === 0) return false
    return staffList.every(name => isStaffDone(row, role, name))
}

const isProjectAllDone = (row) => {
    const roles = getSortedRoles(row)
    if (roles.length === 0) return false
    return roles.every(r => isRoleAllDone(row, r))
}

const getTooltip = (row, role, staffName) => {
    return isStaffDone(row, role, staffName) 
        ? `${staffName}: 完成于 ${row.progress[role][staffName]}` 
        : `${staffName}: 进行中`
}

const markStaffDone = async (row, role, staffName) => {
    let newProgress = JSON.parse(JSON.stringify(row.progress || {}))
    if (!newProgress[role]) newProgress[role] = {}
    if (newProgress[role][staffName]) return // 列表页只能标记完成，不能取消

    newProgress[role][staffName] = new Date().toLocaleString()

    try {
        await axios.post('http://127.0.0.1:5000/api/projects', { ...row, progress: newProgress })
        emit('refresh')
    } catch (e) { ElMessage.error('更新失败') }
}

const openFolder = async (path) => {
    if (!path) return ElMessage.warning('未设置路径')
    try { await axios.post('http://127.0.0.1:5000/api/open-folder', { path }) } catch { ElMessage.error('路径无效') }
}

// --- 展开逻辑 ---
const isLongRole = (role) => role.startsWith('调教 (') // 判断是否为长命名的调教工种
const getShortName = (role) => isLongRole(role) ? '调教' : role
const toggleExpand = (pid, role) => {
    if (!isLongRole(role)) return
    const key = `${pid}_${role}`
    expandedStates.value[key] = !expandedStates.value[key]
}
const isExpanded = (pid, role) => !!expandedStates.value[`${pid}_${role}`]
</script>

<style scoped>
.progress-list { display: flex; flex-direction: column; gap: 8px; }
.progress-row-container { border-bottom: 1px dashed #eee; padding-bottom: 5px; }
.progress-row { display: flex; align-items: center; gap: 10px; }

/* 靠左对齐，宽度自适应但有最小宽度 */
.role-name { 
    font-size: 13px; font-weight: bold; color: #666; 
    min-width: 80px; text-align: left; /* 核心修改：靠左 */
    user-select: none;
}
.role-name.role-all-done { color: #67C23A; } 
.role-name.clickable { cursor: pointer; color: #409EFF; }
.role-name.clickable:hover { text-decoration: underline; }

.role-detail-info {
    margin-left: 20px; font-size: 11px; color: #999; margin-top: 2px;
    background: #f9f9f9; padding: 2px 5px; border-radius: 3px; display: inline-block;
}

.staff-progress-group { display: flex; flex-wrap: wrap; gap: 6px; flex: 1; }
.staff-step {
    padding: 2px 8px; border-radius: 4px; border: 1px solid #dcdfe6; color: #606266;
    font-size: 11px; cursor: pointer; user-select: none; background: #fff; transition: all 0.2s;
}
.staff-step:hover { border-color: #409EFF; color: #409EFF; }
.staff-step.done { background: #67C23A; color: white; border-color: #67C23A; cursor: default; }

.action-column { display: flex; flex-direction: column; gap: 5px; }
.action-btn { width: 100%; margin-left: 0 !important; border-radius: 12px; justify-content: center; padding: 0; height: 28px; font-size: 12px; }
</style>