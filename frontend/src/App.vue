  <template>
    <a-layout>
      <a-layout-header class="app-header">
        <div class="header-left">
          <div class="logo" @click="goHome"> Knowledge Organizer</div>
          <div class="tagline"> 个人知识管理 · 快速提取 · 可视化</div>
        </div>

        <div class="header-right">
          <a-menu mode="horizontal" theme="dark" :selectedKeys="[active]" class="main-menu">
            <a-menu-item key="/input">
              <HomeOutlined style="margin-right:3px;" />
              <router-link to="/input"> 输入 </router-link>
            </a-menu-item>
            <a-menu-item key="/list">
              <UnorderedListOutlined style="margin-right:3px;" />
              <router-link to="/list"> 列表 </router-link>
            </a-menu-item>
            <a-menu-item key="/about">
              <router-link to="/about"> 关于 </router-link>
            </a-menu-item>
          </a-menu>
          <div class="user-area">
            <template v-if="username">
              <a-dropdown>
                <template #overlay>
                  <a-menu @click="onUserMenuClick">
                    <a-menu-item key="change">修改密码</a-menu-item>
                    <a-menu-item key="logout">登出</a-menu-item>
                  </a-menu>
                </template>
                <a-button type="link" class="username-btn">
                  <span class="username-text">{{ username }}<DownOutlined style="margin-left:2px;" /></span>
                </a-button>
              </a-dropdown>
            </template>
            <template v-else>
              <a-menu mode="horizontal" theme="dark" :selectedKeys="[active]" class="main-menu">
                <a-menu-item key="/login"><router-link to="/login">登录</router-link></a-menu-item>
                <a-menu-item key="/register"><router-link to="/register">注册</router-link></a-menu-item>
              </a-menu>
            </template>
          </div>
        </div>
      </a-layout-header>
      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeOutlined, UnorderedListOutlined, DownOutlined } from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()

const username = ref('')

function handleAuthLoginEvent(e) {
  username.value = (e && e.detail && e.detail.username) || localStorage.getItem('username') || ''
}

onMounted(() => {
  username.value = localStorage.getItem('username') || ''
  window.addEventListener('auth:login', handleAuthLoginEvent)
})

onBeforeUnmount(() => {
  window.removeEventListener('auth:login', handleAuthLoginEvent)
})

const active = computed(() => {
  if (route.path.startsWith('/list')) return '/list'
  if (route.path === '/') return '/list'
  if (route.path.startsWith('/about')) return '/about'
  if (route.path.startsWith('/login')) return '/login'
  if (route.path.startsWith('/register')) return '/register'
  return ''
})

function goHome() { router.push('/') }
function doLogout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('username')
  username.value = ''
  router.push('/login')
}

function onUserMenuClick({ key }) {
  if (key === 'change') {
    router.push('/change-password')
  } else if (key === 'logout') {
    doLogout()
  }
}
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

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
}

.user-area a {
  color: #fff;
}

.username-text {
  color: #fff;
  font-weight: 600;
}

.username-btn {
  padding: 0;
  height: 32px;
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