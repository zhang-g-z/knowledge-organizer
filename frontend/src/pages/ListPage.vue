<template>
  <a-card>
    <div class="page-header">
      <div class="page-header-left">
        <h2 style="margin:0">条目列表</h2>
        <div class="muted">共 {{ items.length }} 条 · 第 {{ page }} 页</div>
      </div>

      <div class="page-header-right">
        <a-input-search v-model:value="keyword" placeholder="搜索标题或描述" @search="onSearch" style="width:320px" />
        <a-space style="margin-left:12px">
          <a-button type="primary" icon="" @click="newItem">
            <PlusOutlined /> 新建
          </a-button>
          <a-button icon="" @click="refresh">
            <ReloadOutlined />
          </a-button>
        </a-space>
      </div>
    </div>

    <div v-if="isEmpty" style="text-align:center; padding:48px 0">
      <a-empty description="暂无条目">
        <a-button type="primary" @click="newItem">创建第一个条目</a-button>
      </a-empty>
    </div>

  <a-table v-else :dataSource="items" rowKey="id" :pagination="false" style="width:100%" :loading="loading" :rowClassName="rowClassName">
      <!-- 第一列：标题，20% -->
      <a-table-column title="标题" dataIndex="title" key="title" width="20%">
        <template #default="{ text, record }">
          <div style="font-weight:600">{{ record.title || '（无标题）' }}</div>
          <div style="color:var(--ant-gray-7); margin-top:4px"><small>{{ record.description }}</small></div>
        </template>
      </a-table-column>

      <!-- 第二列：标签，20% -->
      <a-table-column title="标签" dataIndex="tags" key="tags" width="20%">
        <template #default="{ record }">
          <div class="tag-wrap">
            <a-tag v-for="(t, idx) in record.tags" :key="t.id" :color="tagColor(t, idx)">{{ t.name }}</a-tag>
          </div>
        </template>
      </a-table-column>

      <!-- 第三列：摘要，50% -->
      <a-table-column title="摘要" dataIndex="summary" key="summary" width="50%">
        <template #default="{ record }">
          <a-typography-paragraph :ellipsis="{ rows: 3, expandable: true }">{{ record.summary }}</a-typography-paragraph>
        </template>
      </a-table-column>

      <!-- 第四列：操作，10% -->
      <a-table-column title="操作" key="actions" width="10%" align="center">
        <template #default="{ record }">
          <a-space>
            <a-tooltip title="查看原文">
              <a-button type="text" @click="showOriginal(record.id)"><EyeOutlined /></a-button>
            </a-tooltip>
            <a-popconfirm title="确认删除该条目？" ok-text="确认" cancel-text="取消" @confirm="() => remove(record.id)">
              <a-tooltip title="删除">
                <a-button type="text" danger><DeleteOutlined /></a-button>
              </a-tooltip>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table-column>
    </a-table>

    <div style="text-align:right; margin-top:16px">
      <a-pagination :current="page" :pageSize="pageSize" :total="total" @change="onPageChange" />
    </div>
  </a-card>

  <OriginalModal v-if="showModal" :id="currentId" @close="closeModal" />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { EyeOutlined, DeleteOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import api from '../services/api'
import OriginalModal from '../components/OriginalModal.vue'

const items = ref([])
const page = ref(1)
const pageSize = 10
const hasMore = ref(true)
const showModal = ref(false)
const currentId = ref(null)
const keyword = ref('')
const loading = ref(false)

const router = useRouter()

const colors = ['magenta','volcano','orange','gold','green','cyan','blue','geekblue','purple']
const tagColor = (t, idx) => colors[(t.id || idx) % colors.length]

async function load(){
  loading.value = true
  try{
    const res = await api.get('/items', { params: { page: page.value, page_size: pageSize, q: keyword.value } })
    items.value = res.data
    hasMore.value = res.data.length === pageSize
  }catch(err){
    console.error('加载列表失败', err)
  }finally{
    loading.value = false
  }
}

function onPageChange(p){ page.value = p; load() }
function onSearch(){ page.value = 1; load() }

function showOriginal(id){ currentId.value = id; showModal.value = true }

async function remove(id){
  try{
    await api.delete(`/items/${id}`)
    load()
  }catch(err){
    console.error('删除失败', err)
  }
}

function closeModal(){ showModal.value = false; currentId.value = null }

function newItem(){
  // push to input page if available
  router.push('/input')
}

function refresh(){ load() }

const total = computed(() => {
  return page.value * pageSize + (hasMore.value ? pageSize : 0)
})

const isEmpty = computed(() => !loading.value && items.value.length === 0)

function rowClassName(record, index){
  return index % 2 === 1 ? 'table-row-odd' : ''
}

onMounted(load)
</script>

<style scoped>
/* 轻量自定义：让卡片和表格更紧凑 */
.ant-card { padding: 16px; }
.ant-table td { padding: 12px 16px; vertical-align: middle; }
.ant-table td div { word-break: break-word; }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
.page-header-left { display:flex; flex-direction:column }
.page-header-left .muted { color: rgba(0,0,0,0.45); font-size:12px }
.page-header-right { display:flex; align-items:center }
.table-row-odd { background: #fafafa }
.tag-wrap { display:flex; flex-wrap:wrap; gap:6px }
</style>