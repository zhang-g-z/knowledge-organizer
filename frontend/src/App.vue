  <template>
    <a-layout>
      <a-layout-header class="app-header">
        <div class="header-left">
          <div class="logo" @click="goHome"> Knowledge Organizer</div>
          <div class="tagline"> 个人知识管理 · 快速提取 · 可视化</div>
        </div>

        <div class="header-right">
          <a-menu mode="horizontal" theme="dark" :selectedKeys="[active]" class="main-menu">
            <a-menu-item key="/">
              <HomeOutlined />
              <router-link to="/"> 输入 </router-link>
            </a-menu-item>
            <a-menu-item key="/list">
              <UnorderedListOutlined />
              <router-link to="/list"> 列表 </router-link>
            </a-menu-item>
            <a-menu-item key="/about">
              <router-link to="/about"> 关于 </router-link>
            </a-menu-item>
          </a-menu>
        </div>
      </a-layout-header>
      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeOutlined, UnorderedListOutlined } from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()

const active = computed(() => {
  if (route.path.startsWith('/list')) return '/list'
  if (route.path === '/' || route.path.startsWith('/input')) return '/'
  if (route.path.startsWith('/about')) return '/about'
  return ''
})

function goHome() { router.push('/') }
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  flex-direction: column;
  color: #fff
}

.logo {
  font-size: 20px;
  font-weight: 700;
  cursor: pointer;
  line-height: 24px;
}

.tagline {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
  line-height: 14px;
}

.header-right {
  display: flex;
  align-items: center
}

.main-menu {
  background: transparent;
  border-bottom: none
}

.main-menu a {
  color: inherit
}

.app-content {
  padding: 24px;
  min-height: calc(100vh - 64px);
  background: #f0f2f5
}

/* Make router-link inside menu inherit styles and remove default anchor style */
.main-menu .ant-menu-item a {
  color: inherit;
  display: inline-block
}

@media (max-width: 600px) {
  .header-left {
    display: flex;
    flex-direction: row;
    align-items: center
  }

  .tagline {
    display: none
  }

  .logo {
    font-size: 16px
  }
}
</style>