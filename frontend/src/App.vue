<template>
  <div class="main-layout">
    <div class="nav-header">
      <div class="brand">VocaLog PMS</div>
      <div class="actions">
        <template v-if="view === 'projects'">
            <el-button type="info" plain @click="view = 'singers'">
            <el-icon><User /></el-icon> 录入歌手
            </el-button>
            <el-button type="primary" @click="openCreate">
            <el-icon><Plus /></el-icon> 新建工程
            </el-button>
        </template>
      </div>
    </div>

    <div class="content-body">
        <SingerManager 
            v-if="view === 'singers'" 
            @back="view = 'projects'" 
        />
        
        <div v-else>
            <div style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <h3>工程列表</h3>
            </div>
            
            <ProjectList 
                :projects="projects" 
                @refresh="loadProjects" 
                @edit="openEdit" 
                @export="openExport"
            />
        </div>
    </div>

    <ProjectDialog 
        v-model:visible="showDialog" 
        :editData="currentEdit" 
        :singers="singers"
        @refresh="loadProjects"
    />

    <StaffExport
        v-model:visible="showExport"
        :project="currentEdit"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { User, Plus } from '@element-plus/icons-vue'
// 引入所有组件
import SingerManager from './components/SingerManager.vue'
import ProjectList from './components/ProjectList.vue'
import ProjectDialog from './components/ProjectDialog.vue'
import StaffExport from './components/StaffExport.vue'

// 状态管理
const view = ref('projects') // 当前视图: 'projects' 或 'singers'
const projects = ref([])
const singers = ref([])

const showDialog = ref(false)
const showExport = ref(false)
const currentEdit = ref(null)

// 加载工程列表
const loadProjects = async () => {
    try {
        const res = await axios.get('http://127.0.0.1:5000/api/projects')
        projects.value = res.data
    } catch (e) {
        console.error("加载工程失败", e)
    }
}

// 加载歌手列表（传给 ProjectDialog 做级联选择用）
const loadSingers = async () => {
    try {
        const res = await axios.get('http://127.0.0.1:5000/api/singers')
        singers.value = res.data
    } catch (e) {
        console.error("加载歌手失败", e)
    }
}

// 打开新建窗口
const openCreate = () => {
    currentEdit.value = null
    showDialog.value = true
    loadSingers() // 每次打开都刷新一下歌手数据，防止有新录入的
}

// 打开编辑窗口
const openEdit = (row) => {
    currentEdit.value = row
    showDialog.value = true
    loadSingers()
}

// 打开导出窗口
const openExport = (row) => {
    currentEdit.value = row
    showExport.value = true
}

// 初始化
onMounted(() => {
    loadProjects()
    loadSingers()
})
</script>

<style>
body { margin: 0; font-family: 'Helvetica Neue', sans-serif; background: #f0f2f5; }
.nav-header { 
    height: 60px; background: white; display: flex; justify-content: space-between; align-items: center; 
    padding: 0 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
}
.brand { font-size: 20px; font-weight: bold; color: #409EFF; }
.content-body { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
</style>