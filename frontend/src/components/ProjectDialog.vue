<template>
  <el-dialog 
    :model-value="visible" 
    :title="isEdit ? '编辑工程详情' : '新建工程'" 
    width="1000px" 
    :close-on-click-modal="false"
    @close="closeDialog"
  >
    <el-form :model="form" label-width="100px">
      
      <el-form-item label="工程名称">
        <el-input v-model="form.title" placeholder="请输入歌曲标题"></el-input>
      </el-form-item>

      <div v-if="isEdit">
        <el-form-item label="本地目录">
          <div style="display: flex; gap: 10px; width: 100%;">
              <el-input 
                v-model="form.path" 
                :placeholder="isElectron ? '点击右侧按钮选择目录' : '例如: W:\\Works\\Vocaloid...'"
                :readonly="isElectron" 
              ></el-input>
              <el-button v-if="isElectron" type="primary" icon="Folder" @click="handleSelectFolder">选择目录</el-button>
          </div>
          <div v-if="!isElectron" style="font-size: 12px; color: #999; margin-top: 5px;">
             提示：移动端或Web端无法直接读取绝对路径，请手动粘贴。
          </div>
        </el-form-item>

        <el-divider content-position="left">虚拟歌手声库 ({{ form.singer.length }})</el-divider>
        
        <div class="singer-tags">
            <el-tag v-for="(s, idx) in form.singer" :key="idx" closable size="large" @close="removeSinger(idx)" style="margin-right: 10px; margin-bottom: 5px;">
                {{ s }}
            </el-tag>
        </div>

        <div style="display: flex; align-items: center; margin-top: 10px;">
            <el-cascader 
                v-model="tempSingerValue" 
                :options="singerOptions" 
                placeholder="选择歌手/语言/引擎/声库"
                style="width: 450px; margin-right: 10px;"
                separator=" / "
            />
            <el-button type="primary" @click="addSinger" :disabled="!tempSingerValue || tempSingerValue.length !== 4">添加声库</el-button>
        </div>

        <el-divider content-position="left">STAFF 名单分配</el-divider>
        
        <div class="staff-list-container">
           <div v-for="role in sortedDynamicRoles" :key="role" class="staff-row-item">
              <div class="role-label-area">
                  <span class="role-name">{{ role }}</span>
              </div>
              
              <div class="staff-names-area">
                  <div v-for="(name, nIdx) in (form.staff[role] || [])" :key="nIdx" class="staff-entry">
                      <span class="staff-name">{{ name }}</span>
                      
                      <el-tooltip v-if="getStaffProgress(role, name)" content="点击重置为未完成" placement="top">
                          <span class="status-badge done" @click="resetStaffProgress(role, name)">
                              √ {{ formatTime(getStaffProgress(role, name)) }}
                          </span>
                      </el-tooltip>
                      <span v-else class="status-badge todo">未完成</span>

                      <span class="remove-btn" @click="removeStaff(role, nIdx)">×</span>
                  </div>
                  
                  <div class="input-wrapper">
                    <el-input 
                        v-model="tempStaffInput[role]" 
                        placeholder="Staff昵称" 
                        size="small"
                        style="width: 120px;"
                        @keyup.enter="addStaff(role)"
                    ></el-input>
                    <el-button type="primary" link size="small" @click="addStaff(role)">添加</el-button>
                  </div>
              </div>
           </div>
        </div>
      </div>

    </el-form>

    <template #footer>
      <el-button type="danger" v-if="isEdit" @click="handleDelete" style="float: left">删除工程</el-button>
      <el-button @click="closeDialog">取消</el-button>
      <el-button type="primary" @click="handleSave">{{ isEdit ? '保存修改' : '立即创建' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder } from '@element-plus/icons-vue'
import { STAFF_ROLES, sortRoles } from '../utils/constants'

const MAP = { LANG: { CHN: '中文', ENG: '英文', JPN: '日语', KOR: '韩语' }, ENGINE: { V: 'VOCALOID', SV: 'Synthesizer V', ACE: 'ACE Studio', XS: 'X Studio', UT: 'Utau', DV: 'DeepVocal', CV: 'CeVIO', MT: 'MUTA', VS: 'VoiSona', PS: 'Piapro Studio', AS: 'AISingers', SK: 'Sharpkey' } }

// 专门用于显示的映射（Synthesizer V）
const VERSION_DISPLAY_MAP = {
    SV: { 'R1': 'Editor', 'R2S1': 'Studio', 'R2S2': 'Studio 2' }
}

const props = defineProps(['visible', 'editData', 'singers'])
const emit = defineEmits(['update:visible', 'refresh'])

const form = reactive({ id: null, title: '', path: '', staff: {}, progress: {}, singer: [] })
const tempSingerValue = ref([]) 
const tempStaffInput = reactive({}) 
const isElectron = ref(false)

const isEdit = computed(() => !!form.id)

onMounted(() => { isElectron.value = window.electronAPI !== undefined })

const handleSelectFolder = async () => {
    if (!isElectron.value) return
    const path = await window.electronAPI.selectFolder()
    if (path) form.path = path
}

const singerOptions = computed(() => {
    return props.singers.map(s => ({
        value: s.name, label: s.name,
        children: s.langs.map(l => ({
            value: MAP.LANG[l] || l, label: MAP.LANG[l] || l,
            children: (() => {
                const vbs = s.voicebanks[l] || []
                const engines = [...new Set(vbs.map(v => v.engine))]
                return engines.map(eng => ({
                    value: MAP.ENGINE[eng], label: MAP.ENGINE[eng],
                    children: vbs.filter(v => v.engine === eng).map(v => {
                        // 1. 获取显示用的版本号 (Editor/Studio) 或 原版本号
                        let displayVer = v.version
                        if (VERSION_DISPLAY_MAP[eng] && VERSION_DISPLAY_MAP[eng][v.version]) {
                            displayVer = VERSION_DISPLAY_MAP[eng][v.version]
                        }

                        // 2. 处理无名声库占位符
                        const displayName = v.name ? v.name : '-'
                        // 3. 构建显示 Label
                        const labelStr = displayVer === '1' ? displayName : `${displayVer} : ${displayName}`

                        return {
                            // Value 传完整的 displayVer，这样生成的 Tag 也会显示为 Studio
                            value: { ver: displayVer, name: displayName }, 
                            label: labelStr
                        }
                    })
                }))
            })()
        }))
    }))
})

const sortedDynamicRoles = computed(() => {
    const roles = new Set(STAFF_ROLES) 
    roles.delete('调教')
    if (form.singer && form.singer.length > 0) {
        form.singer.forEach(s => roles.add(`调教 (${s})`))
    } else {
        roles.add('调教')
    }
    return sortRoles(Array.from(roles))
})

watch(() => props.visible, (val) => {
    if (val) {
        Object.keys(tempStaffInput).forEach(key => delete tempStaffInput[key])
        tempSingerValue.value = []

        if (props.editData) {
            const d = JSON.parse(JSON.stringify(props.editData))
            form.id = d.id
            form.title = d.title
            form.path = d.path || ''
            form.staff = d.staff || {}
            form.progress = d.progress || {}
            form.singer = Array.isArray(d.singer) ? d.singer : []
            sortedDynamicRoles.value.forEach(role => {
                if (!form.staff[role]) form.staff[role] = []
            })
        } else {
            form.id = null
            form.title = ''; form.path = ''; form.staff = {}; form.progress = {}; form.singer = []
        }
    }
})

const addSinger = () => {
    if (tempSingerValue.value.length === 4) {
        const [name, lang, eng, vbObj] = tempSingerValue.value
        const verStr = vbObj.ver === '1' ? '' : ` ${vbObj.ver}`
        const str = `${name} - ${lang} - ${eng}${verStr} : ${vbObj.name}`
        if (!form.singer.includes(str)) form.singer.push(str)
        tempSingerValue.value = [] 
    }
}

const removeSinger = (idx) => form.singer.splice(idx, 1)

const addStaff = (role) => {
    const val = tempStaffInput[role]
    if (!val || !val.trim()) return
    if (!form.staff[role]) form.staff[role] = []
    form.staff[role].push(val.trim())
    tempStaffInput[role] = '' 
}

const removeStaff = (role, idx) => form.staff[role].splice(idx, 1)

const getStaffProgress = (role, name) => {
    try { return form.progress[role][name] } catch { return null }
}

const resetStaffProgress = (role, name) => {
    if (form.progress[role] && form.progress[role][name]) {
        delete form.progress[role][name]
        form.progress = { ...form.progress }
    }
}

const formatTime = (timeStr) => timeStr ? timeStr.split(' ')[0] : ''

const handleSave = async () => {
    if (!form.title) return ElMessage.warning('请填写标题')
    const payload = JSON.parse(JSON.stringify(form))
    try {
        await axios.post('http://127.0.0.1:5000/api/projects', payload)
        ElMessage.success('保存成功')
        closeDialog()
        emit('refresh')
    } catch (e) { ElMessage.error('保存失败') }
}

const handleDelete = () => {
    ElMessageBox.confirm('确定删除该工程吗？', '警告', { type: 'warning' }).then(async () => {
        await axios.delete(`http://127.0.0.1:5000/api/projects/${form.id}`)
        closeDialog()
        emit('refresh')
    })
}

const closeDialog = () => emit('update:visible', false)
</script>

<style scoped>
.staff-list-container { display: flex; flex-direction: column; gap: 10px; }
.staff-row-item { display: flex; align-items: flex-start; border-bottom: 1px solid #eee; padding-bottom: 8px; }
.role-label-area { 
    width: auto; min-width: 60px; margin-right: 15px; 
    font-weight: bold; color: #555; flex-shrink: 0; padding-top: 5px; 
}
.staff-names-area { flex: 1; display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }

.staff-entry {
    display: flex; align-items: center; gap: 5px;
    background: #fff; border: 1px solid #dcdfe6; 
    padding: 3px 8px; border-radius: 4px; font-size: 13px;
}
.status-badge {
    font-size: 11px; padding: 1px 4px; border-radius: 3px; cursor: pointer; user-select: none;
}
.status-badge.done { background: #f0f9eb; color: #67C23A; border: 1px solid #e1f3d8; }
.status-badge.done:hover { background: #ffebeb; color: #F56C6C; border-color: #fde2e2; }
.status-badge.todo { background: #f4f4f5; color: #909399; }

.remove-btn { cursor: pointer; color: #C0C4CC; font-weight: bold; margin-left: 5px; }
.remove-btn:hover { color: #F56C6C; }

.input-wrapper { display: flex; align-items: center; gap: 5px; }
</style>