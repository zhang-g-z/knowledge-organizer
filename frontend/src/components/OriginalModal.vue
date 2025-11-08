<template>
  <div class="overlay">
    <div class="modal">
      <h3>原文</h3>
      <div v-if="loading">加载中...</div>
      <pre v-else style="white-space:pre-wrap">{{ original }}</pre>
      <button @click="$emit('close')">关闭</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../services/api'
import { toRef } from 'vue'

const props = defineProps({ id: Number })
const original = ref('')
const loading = ref(false)

async function load(){
  if(!props.id) return
  loading.value = true
  try{
    const res = await api.get(`/items/${props.id}/original`)
    original.value = res.data.original_text
  }catch(err){
    original.value = '加载失败'
  }finally{
    loading.value = false
  }
}

watch(() => props.id, () => load(), { immediate: true })
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center;
}
.modal { background: white; padding: 16px; width: 80%; max-height: 80%; overflow:auto; border-radius:6px; }
</style>