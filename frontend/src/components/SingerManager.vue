<template>
  <el-card>
    <template #header>
      <div class="header-actions">
        <el-button @click="$emit('back')"> &lt; 返回工程列表</el-button>
        <span class="title">歌手管理</span>
        <el-button type="primary" @click="createNew">新建歌手</el-button>
      </div>
    </template>
    
    <div style="margin-bottom: 20px;">
        <span style="font-size: 12px; color: #999;">点击下方标签进行修改:</span><br/>
        <el-space wrap>
            <el-tag 
                v-for="(s, idx) in singers" :key="idx" 
                :color="s.color ? '#' + s.color : ''" 
                :effect="s.color ? 'dark' : 'light'"
                style="cursor: pointer; border: none;"
                @click="editSinger(idx)"
            >
                {{ s.name || '-' }}
            </el-tag>
        </el-space>
    </div>

    <el-divider />

    <el-form :model="form" label-width="80px">
      <el-row :gutter="20">
        <el-col :span="8"><el-form-item label="中文名"><el-input v-model="form.name"></el-input></el-form-item></el-col>
        <el-col :span="8"><el-form-item label="英文名"><el-input v-model="form.eng_name"></el-input></el-form-item></el-col>
        <el-col :span="8"><el-form-item label="代表色"><el-input v-model="form.color" placeholder="不带#"></el-input></el-form-item></el-col>
      </el-row>

      <div v-for="(langItem, lIdx) in form.langsData" :key="lIdx" class="lang-block">
        <el-row>
            <el-col :span="6">
                <el-select v-model="langItem.lang" placeholder="语言">
                    <el-option v-for="(v, k) in MAP.LANG" :key="k" :label="v" :value="k"></el-option>
                </el-select>
            </el-col>
            <el-col :span="18" style="text-align: right;">
                <el-button type="danger" link @click="removeLang(lIdx)">删除语言</el-button>
            </el-col>
        </el-row>
        <div class="vb-list">
            <div v-for="(vb, vIdx) in langItem.vbs" :key="vIdx" style="margin-top: 5px; display: flex; gap: 5px;">
                <el-select v-model="vb.engine" placeholder="引擎" style="width: 130px" @change="handleEngineReset(vb)">
                    <el-option v-for="(v, k) in MAP.ENGINE" :key="k" :label="v" :value="k"></el-option>
                </el-select>
                
                <el-select v-if="ENGINE_OPTIONS[vb.engine]" v-model="vb.version" style="width: 100px">
                    <el-option v-for="o in ENGINE_OPTIONS[vb.engine]" :key="o.code" :label="o.label" :value="o.code"></el-option>
                </el-select>
                <el-input v-else v-model="vb.version" disabled style="width: 100px"></el-input>
                
                <el-input v-model="vb.name" placeholder="声库名 (可留空)" style="width: 140px"></el-input>
                
                <el-button type="danger" plain size="small" @click="removeVb(lIdx, vIdx)">删除</el-button>
            </div>
            <div style="margin-top: 5px;">
                <el-button type="primary" link size="small" @click="addVb(lIdx)">+ 添加声库</el-button>
            </div>
        </div>
      </div>
      
      <el-button @click="addLangBlock" style="width: 100%; margin: 10px 0;">+ 添加语言区域</el-button>
      
      <div style="display: flex; gap: 10px; margin-top: 10px;">
          <el-button v-if="editIndex !== -1" type="danger" @click="deleteSinger" style="width: 30%;">删除该歌手</el-button>
          
          <el-button type="success" @click="saveAll" style="flex: 1;">保存全部修改</el-button>
      </div>

    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const MAP = { LANG: { CHN: '中文', ENG: '英文', JPN: '日语', KOR: '韩语' }, ENGINE: { V: 'VOCALOID', SV: 'Synthesizer V', ACE: 'ACE Studio', XS: 'X Studio', UT: 'Utau', DV: 'DeepVocal', CV: 'CeVIO', MT: 'MUTA', VS: 'VoiSona', PS: 'Piapro Studio', AS: 'AISingers', SK: 'Sharpkey' } }

const ENGINE_OPTIONS = { 
    V: [
        {code:'1',label:'1'}, {code:'2',label:'2'}, {code:'3',label:'3'},
        {code:'4',label:'4'}, {code:'5',label:'5'}, {code:'6',label:'6'}, 
        {code:'AI',label:'AI'}
    ], 
    SV: [{code:'R1',label:'Editor'},{code:'R2S1',label:'Studio'},{code:'R2S2',label:'Studio 2'}], 
    ACE: [{code:'1',label:'V1'},{code:'2',label:'V2'}], 
    XS: [{code:'1',label:'1.0'},{code:'2',label:'2.0'},{code:'3',label:'3.0'}], 
    PS: [{code:'E',label:'Edition'},{code:'N',label:'NT'}], 
    CV: [{code:'CS',label:'Creative Studio'},{code:'AI',label:'AI'}] 
}

const singers = ref([])
const editIndex = ref(-1) 

const form = reactive({ name: '', eng_name: '', color: '', langsData: [] })

const fetchSingers = async () => {
    try {
        const res = await axios.get('http://127.0.0.1:5000/api/singers')
        singers.value = res.data
    } catch(e) { console.error(e) }
}

const createNew = () => {
    editIndex.value = -1
    Object.assign(form, { name: '', eng_name: '', color: '', langsData: [] })
}

const editSinger = (idx) => {
    editIndex.value = idx
    const s = singers.value[idx]
    form.name = s.name
    form.eng_name = s.eng_name
    form.color = s.color
    form.langsData = s.langs.map(l => ({
        lang: l,
        vbs: JSON.parse(JSON.stringify(s.voicebanks[l] || []))
    }))
}

const addLangBlock = () => form.langsData.push({ lang: '', vbs: [] })
const removeLang = (i) => form.langsData.splice(i, 1)
const addVb = (i) => form.langsData[i].vbs.push({ engine: 'V', version: '1', name: '' })
const removeVb = (li, vi) => form.langsData[li].vbs.splice(vi, 1)
const handleEngineReset = (vb) => { vb.version = (ENGINE_OPTIONS[vb.engine]?.[0]?.code) || '1' }

const saveAll = async () => {
    const payloadSinger = {
        name: form.name, eng_name: form.eng_name, color: form.color,
        langs: form.langsData.map(l => l.lang),
        voicebanks: {}
    }
    form.langsData.forEach(l => { payloadSinger.voicebanks[l.lang] = l.vbs })

    let newSingersList = [...singers.value]
    if (editIndex.value === -1) {
        newSingersList.push(payloadSinger)
    } else {
        newSingersList[editIndex.value] = payloadSinger
    }

    try {
        await axios.post('http://127.0.0.1:5000/api/singers', newSingersList)
        ElMessage.success('保存成功')
        fetchSingers()
        createNew() 
    } catch(e) { ElMessage.error('保存失败') }
}

// 新增：删除歌手逻辑
const deleteSinger = async () => {
    if (editIndex.value === -1) return
    
    ElMessageBox.confirm('确定要删除这位歌手吗？此操作不可恢复。', '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(async () => {
        // 从列表中移除
        const newSingersList = [...singers.value]
        newSingersList.splice(editIndex.value, 1)
        
        try {
            // 同步到后端
            await axios.post('http://127.0.0.1:5000/api/singers', newSingersList)
            ElMessage.success('删除成功')
            fetchSingers()
            createNew() // 重置表单
        } catch(e) { ElMessage.error('删除失败') }
    }).catch(() => {})
}

onMounted(fetchSingers)
</script>

<style scoped>
.header-actions { display: flex; align-items: center; gap: 10px; }
.title { font-weight: bold; margin-right: auto; margin-left: 10px; font-size: 16px; }
.lang-block { border: 1px dashed #ddd; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
.vb-list { padding-left: 20px; }
</style>