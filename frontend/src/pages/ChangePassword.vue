<template>
    <a-card title="修改密码" style="max-width:480px;margin:24px auto;">
        <a-form @submit.prevent="doChange" layout="vertical">
            <a-form-item label="原密码" :validateStatus="fieldStatus('oldPassword')" :help="errors.oldPassword">
                <div class="field-row">
                    <a-input-password v-model:value="oldPassword" @input="onInput('oldPassword')" />
                    <div class="validation">
                        <CheckOutlined v-if="valid.oldPassword" class="ok" />
                        <CloseOutlined v-else-if="touched.oldPassword" class="bad" />
                    </div>
                </div>
            </a-form-item>
            <a-form-item label="新密码" :validateStatus="fieldStatus('newPassword')" :help="errors.newPassword">
                <div class="field-row">
                    <a-input-password v-model:value="newPassword" @input="onInput('newPassword')" />
                    <div class="validation">
                        <CheckOutlined v-if="valid.newPassword" class="ok" />
                        <CloseOutlined v-else-if="touched.newPassword" class="bad" />
                    </div>
                </div>
            </a-form-item>
            <a-form-item label="确认新密码" :validateStatus="fieldStatus('confirmPassword')" :help="errors.confirmPassword">
                <div class="field-row">
                    <a-input-password v-model:value="confirmPassword" @input="onInput('confirmPassword')" />
                    <div class="validation">
                        <CheckOutlined v-if="valid.confirmPassword" class="ok" />
                        <CloseOutlined v-else-if="touched.confirmPassword" class="bad" />
                    </div>
                </div>
            </a-form-item>
            <a-form-item>
                <a-button type="primary" @click="doChange" :loading="submitting">提交</a-button>
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

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const submitting = ref(false)
const router = useRouter()

const touched = reactive({ oldPassword: false, newPassword: false, confirmPassword: false })
const valid = reactive({ oldPassword: false, newPassword: false, confirmPassword: false })
const errors = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

function onInput(field) {
    touched[field] = true
    if (field === 'oldPassword') {
        valid.oldPassword = oldPassword.value.length > 0
        errors.oldPassword = valid.oldPassword ? '' : '请输入旧密码'
    }
    if (field === 'newPassword') {
        valid.newPassword = newPassword.value.length >= 6
        errors.newPassword = valid.newPassword ? '' : '密码至少6位'
        valid.confirmPassword = confirmPassword.value === newPassword.value && confirmPassword.value.length > 0
        errors.confirmPassword = valid.confirmPassword ? '' : '两次密码不一致'
    }
    if (field === 'confirmPassword') {
        valid.confirmPassword = confirmPassword.value === newPassword.value && confirmPassword.value.length > 0
        errors.confirmPassword = valid.confirmPassword ? '' : '两次密码不一致'
    }
}

function fieldStatus(field) {
    if (!touched[field]) return ''
    return valid[field] ? 'success' : 'error'
}

async function doChange() {
    Object.keys(touched).forEach(k => touched[k] = true)
    onInput('oldPassword')
    onInput('newPassword')
    onInput('confirmPassword')

        if (!valid.oldPassword || !valid.newPassword || !valid.confirmPassword) {
            message.info('请修正表单错误后再提交')
            return
        }

    submitting.value = true
    try {
            await api.post('/auth/change_password', { old_password: oldPassword.value, new_password: newPassword.value, confirm_password: confirmPassword.value })
            message.success('修改成功，请重新登录')
        localStorage.removeItem('access_token')
        localStorage.removeItem('username')
        router.push('/login')
    } catch (err) {
        console.error(err)
        const msg = err?.response?.data?.detail || '修改失败'
            message.error(msg)
    } finally {
        submitting.value = false
    }
}
</script>

<style scoped>
.field-row {
    display: flex;
    align-items: center
}

.validation {
    width: 36px;
    display: flex;
    align-items: center;
    justify-content: center
}

.ok {
    color: #52c41a;
    font-size: 16px
}

.bad {
    color: #ff4d4f;
    font-size: 16px
}
</style>
