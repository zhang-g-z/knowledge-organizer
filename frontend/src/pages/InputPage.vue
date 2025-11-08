<template>
  <a-card>
    <div class="input-header">
      <div>
        <h2 style="margin:0">创建条目</h2>
        <div class="muted">将原文粘贴到下面，提交后系统会异步提取并更新条目</div>
      </div>
    </div>

    <a-form layout="vertical">
      <a-form-item label="原文（支持大文本）">
        <a-textarea v-model:value="text" :rows="10" showCount :maxlength="50000" placeholder="在此粘贴/输入你的文本" />
      </a-form-item>

      <a-form-item>
        <a-space>
          <a-button type="primary" :loading="loading" @click="submit">
            <SendOutlined /> 提交并异步提取
          </a-button>
          <a-button @click="clear">清空</a-button>
          <a-button @click="previewLast" v-if="lastItem">查看最近条目</a-button>
        </a-space>
      </a-form-item>
    </a-form>

    <div v-if="lastItem" style="margin-top:16px">
      <a-card title="已创建（异步处理中）" size="small">
        <a-descriptions column="1" bordered>
          <a-descriptions-item label="ID">{{ lastItem.id }}</a-descriptions-item>
          <a-descriptions-item label="状态">{{ lastItem.status }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ lastItem.created_at }}</a-descriptions-item>
        </a-descriptions>

        <div v-if="result" style="margin-top:12px">
          <a-divider />
          <h4>提取结果（完成）</h4>
          <a-descriptions column="1" bordered>
            <a-descriptions-item label="标题">{{ result.title }}</a-descriptions-item>
            <a-descriptions-item label="标签">
              <a-space>
                <a-tag v-for="(t, idx) in result.tags" :key="idx">{{ t }}</a-tag>
              </a-space>
            </a-descriptions-item>
            <a-descriptions-item label="描述">{{ result.description }}</a-descriptions-item>
            <a-descriptions-item label="摘要">{{ result.summary }}</a-descriptions-item>
          </a-descriptions>
        </div>
      </a-card>
    </div>
  </a-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { SendOutlined } from '@ant-design/icons-vue'
import api from '../services/api'
import createWS from '../services/ws'
import { message } from 'ant-design-vue'

const text = ref('')
const loading = ref(false)
const lastItem = ref(null)
const result = ref(null)
let ws = null

async function submit(){
  if(!text.value.trim()) return ;
  loading.value = true
  try{
    const res = await api.post('/items', { text: text.value })
    lastItem.value = res.data
    text.value = ''
  }catch(err){
    // show error message via AntD message
    message.error('提交失败: ' + (err.response?.data?.detail || err.message))
  }finally{
    loading.value = false
  }
}

function clear(){ text.value = '' }

function previewLast(){
  if(!lastItem.value) return
  // fetch latest detail
  api.get(`/items/${lastItem.value.id}`).then(r => {
    lastItem.value = r.data
    if(r.data.status === 'done'){
      result.value = {
        title: r.data.title,
        tags: r.data.tags.map(t => t.name),
        description: r.data.description,
        summary: r.data.summary
      }
    }
  }).catch(e => console.error(e))
}

function handleWsMessage(data){
  if(!lastItem.value) return
  if(data.id === lastItem.value.id){
    api.get(`/items/${data.id}`).then(r => {
      lastItem.value = r.data
      if(r.data.status === 'done'){
        result.value = {
          title: r.data.title,
          tags: r.data.tags.map(t => t.name),
          description: r.data.description,
          summary: r.data.summary
        }
      }
    }).catch(e => console.error(e))
  }
}

onMounted(()=>{
  ws = createWS(handleWsMessage)
})

onBeforeUnmount(()=>{
  if(ws) ws.close()
})
</script>

<style scoped>
.input-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
.muted { color: rgba(0,0,0,0.45); font-size:12px }
.ant-card { padding:16px }
</style>