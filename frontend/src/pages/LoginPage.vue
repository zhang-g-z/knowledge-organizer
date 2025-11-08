<template>
    <a-card title="登录" style="max-width:480px;margin:24px auto;">
        <a-form @submit.prevent="doLogin" layout="vertical">
            <a-form-item label="用户名">
                <a-input v-model:value="username" />
            </a-form-item>
            <a-form-item label="密码">
                <a-input-password v-model:value="password" />
            </a-form-item>
            <a-form-item>
                <a-button type="primary" @click="doLogin">登录</a-button>
            </a-form-item>
        </a-form>
    </a-card>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'

const username = ref('')
const password = ref('')
const router = useRouter()

async function doLogin() {
    try {
        const params = new URLSearchParams()
        params.append('username', username.value)
        params.append('password', password.value)
        params.append('grant_type', '')
        // ensure form-encoded content type so FastAPI's OAuth2PasswordRequestForm can parse it
        const res = await api.post('/auth/token', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })
        const token = res.data.access_token
        localStorage.setItem('access_token', token)
        // store username locally for display in navbar
        localStorage.setItem('username', username.value)
        // notify other components (App) about login
        try { window.dispatchEvent(new CustomEvent('auth:login', { detail: { username: username.value } })) } catch (e) { }
        router.push('/list')
    } catch (err) {
        console.error('login error', err)
        const status = err?.response?.status
        // fallback: some clients/environments can't send form-encoded data properly; try JSON endpoint
        if (status === 422) {
            try {
                const res2 = await api.post('/auth/token_json', { username: username.value, password: password.value })
                const token2 = res2.data.access_token
                localStorage.setItem('access_token', token2)
                localStorage.setItem('username', username.value)
                try { window.dispatchEvent(new CustomEvent('auth:login', { detail: { username: username.value } })) } catch (e) { }
                router.push('/list')
                return
            } catch (err2) {
                    console.error('token_json fallback error', err2)
                    const msg2 = err2?.response?.data?.detail || err2?.message || '登录失败'
                    message.error(msg2)
                return
            }
        }
        const msg = err?.response?.data?.detail || err?.message || '登录失败'
        message.error(msg)
    }
}
</script>

<style scoped>
/* small centered card */
</style>
