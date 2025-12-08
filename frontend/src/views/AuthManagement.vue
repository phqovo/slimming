<template>
  <div class="auth-management-container">
    <el-card class="page-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h2>授权管理</h2>
          <el-button type="primary" @click="showAddDialog" round>
            <el-icon><Plus /></el-icon>
            新增授权
          </el-button>
        </div>
      </template>

      <el-table
        :data="authList"
        style="width: 100%"
        @row-dblclick="handleRowDblClick"
        class="rounded-table"
      >
      <el-table-column prop="auth_type" label="授权类型" width="200">
        <template #default="{ row }">
          {{ getAuthTypeName(row.auth_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="account" label="账号" width="200" />
      <el-table-column label="密码" width="150">
        <template #default>
          **********
        </template>
      </el-table-column>
      <el-table-column label="验证状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.status === 0" type="info">未验证</el-tag>
          <el-tag v-else-if="row.status === 1" type="success">验证成功</el-tag>
          <el-tag v-else-if="row.status === 2" type="danger">验证失败</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" @click="handleVerify(row)">验证</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchAuthList"
        @current-change="fetchAuthList"
      />
    </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="授权类型" prop="auth_type">
          <el-select
            v-model="formData.auth_type"
            placeholder="请选择授权类型"
            :disabled="isEdit"
            style="width: 100%"
          >
            <el-option label="小米运动健康" value="xiaomi_sport" />
          </el-select>
        </el-form-item>
        <el-form-item label="账号" prop="account">
          <el-input v-model="formData.account" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="!isEdit" type="success" @click="handleVerifyInDialog" :loading="verifyLoading">验证</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="授权详情"
      width="500px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="授权类型">
          {{ getAuthTypeName(detailData.auth_type) }}
        </el-descriptions-item>
        <el-descriptions-item label="账号">
          {{ detailData.account }}
        </el-descriptions-item>
        <el-descriptions-item label="密码">
          **********
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatTime(detailData.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatTime(detailData.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getAuthList,
  getAuthDetail,
  createAuth,
  updateAuth,
  deleteAuth,
  verifyAndSaveToken,
  checkVerifyStatus
} from '@/api/auth-management'
import dayjs from 'dayjs'

const authList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const verifyLoading = ref(false)

const dialogVisible = ref(false)
const dialogTitle = ref('新增授权')
const isEdit = ref(false)
const formRef = ref(null)
const formData = ref({
  auth_type: 'xiaomi_sport',
  account: '',
  password: ''
})

const detailDialogVisible = ref(false)
const detailData = ref({})

const formRules = {
  auth_type: [{ required: true, message: '请选择授权类型', trigger: 'change' }],
  account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 授权类型映射
const getAuthTypeName = (type) => {
  const typeMap = {
    xiaomi_sport: '小米运动健康'
  }
  return typeMap[type] || type
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 重置表单
const resetForm = () => {
  formData.value = {
    auth_type: 'xiaomi_sport',
    account: '',
    password: ''
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 获取授权列表
const fetchAuthList = async () => {
  try {
    const res = await getAuthList({
      page: currentPage.value,
      page_size: pageSize.value
    })
    authList.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('获取授权列表失败')
  }
}

// 监听密码字段变化，自动重置验证状态
watch(() => formData.value.password, (newVal, oldVal) => {
  // 编辑模式下，如果密码被修改，重置验证状态提示
  if (isEdit.value && oldVal && newVal !== oldVal) {
    ElMessage.warning('密码已修改，请重新验证')
  }
})

// 显示新增对话框
const showAddDialog = () => {
  dialogTitle.value = '新增授权'
  isEdit.value = false
  dialogVisible.value = true
}

// 双击查看详情
const handleRowDblClick = async (row) => {
  try {
    const res = await getAuthDetail(row.id)
    detailData.value = res
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

// 编辑
const handleEdit = (row) => {
  dialogTitle.value = '编辑授权'
  isEdit.value = true
  formData.value = {
    id: row.id,
    auth_type: row.auth_type,
    account: row.account,
    password: row.password
  }
  dialogVisible.value = true
}

// 验证授权（列表中点击）
const handleVerify = async (row) => {
  try {
    await ElMessageBox.confirm('确定要验证该授权吗？验证成功后将自动保存Token。', '提示', {
      type: 'warning'
    })
    
    loading.value = true
    
    try {
      await verifyAndSaveToken(row.id)
      ElMessage.success('验证成功')
      fetchAuthList()
    } catch (error) {
      console.log('验证错误:', error)
      // 检查是否需要二次验证
      if (error.response?.status === 202) {
        const detail = error.response.data?.detail
        console.log('二次验证详情:', detail)
        
        if (detail && (detail.need_verify || detail.notification_url)) {
          const notificationUrl = detail.notification_url || ''
          const message = detail.message || '需要二次验证'
          
          // 显示二次验证对话框
          ElMessageBox.alert(
            `${message}<br><br>请点击下方链接在新窗口完成验证：<br><br><a href="${notificationUrl}" target="_blank" style="color: #409eff; text-decoration: underline;">点击此处完成验证</a><br><br><strong style="color: #e6a23c;">注意：完成验证后，请手动再次点击“验证”按钮。</strong>`,
            '需要二次验证',
            {
              dangerouslyUseHTMLString: true,
              confirmButtonText: '知道了'
            }
          )
        } else {
          ElMessage.error('验证失败：未获取到验证链接')
        }
      } else {
        const errorMsg = error.response?.data?.detail || error.response?.data?.message || '验证失败'
        ElMessage.error(errorMsg)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

// 对话框中的验证（新增时）
const handleVerifyInDialog = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    verifyLoading.value = true
    let authId = null
    try {
      // 先保存
      const res = await createAuth(formData.value)
      authId = res.id
      console.log('保存成功，ID:', authId)
      ElMessage.success('保存成功，正在验证...')
      
      // 再验证
      console.log('开始验证...')
      const verifyResult = await verifyAndSaveToken(authId)
      console.log('验证结果:', verifyResult)
      ElMessage.success('验证成功')
      
      dialogVisible.value = false
      fetchAuthList()
    } catch (error) {
      console.log('=== 捕获到错误 ===', error)
      console.log('错误类型:', error.constructor.name)
      console.log('响应状态:', error.response?.status)
      console.log('响应数据:', error.response?.data)
      
      // 检查是否需要二次验证
      if (error.response?.status === 202) {
        console.log('=== 检测到 202 状态码 ===')
        const detail = error.response.data?.detail
        console.log('二次验证详情:', detail)
        
        if (detail && (detail.need_verify || detail.notification_url)) {
          const notificationUrl = detail.notification_url || ''
          const message = detail.message || '需要二次验证'
          
          console.log('=== 准备显示二次验证对话框 ===')
          console.log('消息:', message)
          console.log('验证链接:', notificationUrl)
          
          // 显示二次验证对话框
          ElMessageBox.alert(
            `${message}<br><br>请点击下方链接在新窗口完成验证：<br><br><a href="${notificationUrl}" target="_blank" style="color: #409eff; text-decoration: underline;">点击此处完成验证</a><br><br><strong style="color: #e6a23c;">注意：完成验证后，请手动再次点击“验证”按钮。</strong>`,
            '需要二次验证',
            {
              dangerouslyUseHTMLString: true,
              confirmButtonText: '知道了'
            }
          )
        } else {
          console.log('=== detail 数据不完整 ===')
          ElMessage.error('验证响应数据异常')
        }
      } else {
        console.log('=== 非 202 错误 ===')
        ElMessage.error(error.response?.data?.detail || '验证失败')
      }
    } finally {
      verifyLoading.value = false
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      if (isEdit.value) {
        await updateAuth(formData.value.id, {
          account: formData.value.account,
          password: formData.value.password
        })
        ElMessage.success('更新成功')
      } else {
        await createAuth(formData.value)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchAuthList()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      loading.value = false
    }
  })
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该授权吗？', '提示', {
      type: 'warning'
    })
    await deleteAuth(row.id)
    ElMessage.success('删除成功')
    fetchAuthList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  console.log('=== 授权管理页面已加载 [有调试日志版本] ===')
  fetchAuthList()
})
</script>

<style scoped>
.auth-management-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-card {
  border-radius: 16px;
  border: none;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.rounded-table {
  border-radius: 12px;
  overflow: hidden;
}

.rounded-table :deep(.el-table__header-wrapper) {
  border-radius: 12px 12px 0 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 对话框圆角 */
:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-bottom: 1px solid #f0f0f0;
}
</style>
