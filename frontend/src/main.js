import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Ant Design Vue (global registration)
import Antd from 'ant-design-vue'
// v4 版本在 package 的 dist 中默认导出 reset.css（不再包含旧的 antd.css 文件）
import 'ant-design-vue/dist/reset.css'

const app = createApp(App)
app.use(router)
app.use(Antd)
app.mount('#app')