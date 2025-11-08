<template>
  <a-card title="注册新用户" style="max-width:600px;margin:24px auto;">
    <a-form @submit.prevent="doRegister" layout="vertical">

      <a-form-item label="用户名" :validateStatus="fieldStatus('username')" :help="errors.username">
        <div class="field-row">
          <a-input v-model:value="username" @input="onInput('username')" />
          <div class="validation">
            <CheckOutlined v-if="valid.username" class="ok" />
            <CloseOutlined v-else-if="touched.username" class="bad" />
          </div>
        </div>
      </a-form-item>

      <a-form-item label="密码" :validateStatus="fieldStatus('password')" :help="errors.password">
        <div class="field-row">
          <a-input-password v-model:value="password" @input="onInput('password')" />
          <div class="validation">
            <CheckOutlined v-if="valid.password" class="ok" />
            <CloseOutlined v-else-if="touched.password" class="bad" />
          </div>
        </div>
      </a-form-item>

      <a-form-item label="确认密码" :validateStatus="fieldStatus('confirmPassword')" :help="errors.confirmPassword">
        <div class="field-row">
          <a-input-password v-model:value="confirmPassword" @input="onInput('confirmPassword')" />
          <div class="validation">
            <CheckOutlined v-if="valid.confirmPassword" class="ok" />
            <CloseOutlined v-else-if="touched.confirmPassword" class="bad" />
          </div>
        </div>
      </a-form-item>

      <a-form-item label="姓名" :validateStatus="fieldStatus('name')" :help="errors.name">
        <div class="field-row">
          <a-input v-model:value="name" @input="onInput('name')" />
          <div class="validation">
            <CheckOutlined v-if="valid.name" class="ok" />
            <CloseOutlined v-else-if="touched.name" class="bad" />
          </div>
        </div>
      </a-form-item>

      <a-form-item label="手机号码" :validateStatus="fieldStatus('phone')" :help="errors.phone">
        <div class="field-row">
          <a-input v-model:value="phone" @input="onInput('phone')" />
          <div class="validation">
            <CheckOutlined v-if="valid.phone" class="ok" />
            <CloseOutlined v-else-if="touched.phone" class="bad" />
          </div>
        </div>
      </a-form-item>

      <a-form-item label="邮箱" :validateStatus="fieldStatus('email')" :help="errors.email">
        <div class="field-row">
          <a-input v-model:value="email" @input="onInput('email')" />
          <div class="validation">
            <CheckOutlined v-if="valid.email" class="ok" />
            <CloseOutlined v-else-if="touched.email" class="bad" />
          </div>
        </div>
      </a-form-item>

      <a-form-item>
        <a-button type="primary" @click="doRegister" :loading="submitting">注册</a-button>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../services/api'
import { useRouter } from 'vue-router'
import { CheckOutlined, CloseOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const name = ref('')
const phone = ref('')
const email = ref('')
const submitting = ref(false)
const touched = reactive({ username: false, password: false, confirmPassword: false, name: false, phone: false, email: false })
const valid = reactive({ username: false, password: false, confirmPassword: false, name: true, phone: false, email: false })
const errors = reactive({ username: '', password: '', confirmPassword: '', name: '', phone: '', email: '' })

const router = useRouter()

function validateEmail(e) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(e)
}

function validatePhone(p) {
  const re = /^\+?\d{7,15}$/
  return re.test(p)
}

function onInput(field) {
  touched[field] = true
  if (field === 'username') {
    valid.username = username.value.length >= 3
    errors.username = valid.username ? '' : '用户名至少3个字符'
  }
  if (field === 'password') {
    valid.password = password.value.length >= 6
    errors.password = valid.password ? '' : '密码至少6位'
    // also refresh confirm validity
    valid.confirmPassword = confirmPassword.value === password.value && confirmPassword.value.length > 0
    errors.confirmPassword = valid.confirmPassword ? '' : '两次密码不一致'
  }
  if (field === 'confirmPassword') {
    valid.confirmPassword = confirmPassword.value === password.value && confirmPassword.value.length > 0
    errors.confirmPassword = valid.confirmPassword ? '' : '两次密码不一致'
  }
  if (field === 'name') {
    valid.name = name.value.length <= 150
    errors.name = valid.name ? '' : '姓名过长'
  }
  if (field === 'phone') {
    valid.phone = validatePhone(phone.value)
    errors.phone = valid.phone ? '' : '手机格式不正确'
  }
  if (field === 'email') {
    valid.email = validateEmail(email.value)
    errors.email = valid.email ? '' : '邮箱格式不正确'
  }
}

function fieldStatus(field) {
  if (!touched[field]) return ''
  return valid[field] ? 'success' : 'error'
}

async function doRegister() {
  // mark all touched
  Object.keys(touched).forEach(k => touched[k] = true)
  // run validations
  onInput('username')
  onInput('password')
  onInput('confirmPassword')
  onInput('name')
  onInput('phone')
  onInput('email')

  if (!valid.username || !valid.password || !valid.confirmPassword || !valid.phone || !valid.email) {
    message.info('请修正表单错误后再提交')
    return
  }

  submitting.value = true
  try {
    await api.post('/auth/register', { username: username.value, password: password.value, name: name.value, phone: phone.value, email: email.value })
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (err) {
    console.error(err)
    const detail = err?.response?.data?.detail
    if (detail && typeof detail === 'string') {
      message.error(detail)
    } else {
      message.error('注册失败')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.field-row { display: flex; align-items: center }
.validation { width: 36px; display:flex; align-items:center; justify-content:center }
.ok { color: #52c41a; font-size: 16px }
.bad { color: #ff4d4f; font-size: 16px }
</style>
