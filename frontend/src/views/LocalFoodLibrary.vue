<template>
  <div class="local-food-library">
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索食物名称"
        class="search-input"
        clearable
        @keyup.enter="loadFoods"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增食物
      </el-button>
    </div>

    <!-- 食物列表 -->
    <div class="food-list">
      <el-table
        :data="foods"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column label="图片" width="100">
          <template #default="{ row }">
            <div class="food-thumb">
              <img :src="row.image_url || defaultImage" :alt="row.name" />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="食物名称" min-width="150" />
        
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.category" size="small">{{ row.category }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="calories" label="热量(千卡/100g)" width="150">
          <template #default="{ row }">
            <span class="calories-text">{{ row.calories }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="protein" label="蛋白质(g)" width="120" />
        <el-table-column prop="carbs" label="碳水(g)" width="120" />
        <el-table-column prop="fat" label="脂肪(g)" width="120" />
        
        <el-table-column label="来源" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_custom ? 'success' : 'info'" size="small">
              {{ row.is_custom ? '自定义' : '系统' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadFoods"
        @size-change="loadFoods"
        class="pagination"
      />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑食物' : '新增食物'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="食物名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入食物名称" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-input v-model="form.category" placeholder="如：主食、蔬菜、水果等" />
        </el-form-item>
        
        <el-form-item label="食物图片">
          <el-upload
            class="food-upload"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
          >
            <img v-if="form.image_url" :src="form.image_url" class="uploaded-image" />
            <el-icon v-else class="upload-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="热量" prop="calories">
              <el-input v-model.number="form.calories" placeholder="千卡/100g">
                <template #append>千卡</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="蛋白质">
              <el-input v-model.number="form.protein" placeholder="g/100g">
                <template #append>g</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="碳水化合物">
              <el-input v-model.number="form.carbs" placeholder="g/100g">
                <template #append>g</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="脂肪">
              <el-input v-model.number="form.fat" placeholder="g/100g">
                <template #append>g</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { getLocalFoods, createLocalFood, updateLocalFood, deleteLocalFood } from '@/api/food'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const searchKeyword = ref('')
const loading = ref(false)
const foods = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const defaultImage = '/default-food.png'

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const submitting = ref(false)

const uploadUrl = import.meta.env.PROD 
  ? 'https://piheqi.com/health/api/v1/food/upload-image'
  : '/health/api/v1/food/upload-image'

const uploadHeaders = {
  Authorization: `Bearer ${userStore.token}`
}

const form = reactive({
  id: null,
  name: '',
  category: '',
  calories: null,
  protein: 0,
  carbs: 0,
  fat: 0,
  image_url: ''
})

const rules = {
  name: [
    { required: true, message: '请输入食物名称', trigger: 'blur' }
  ],
  calories: [
    { required: true, message: '请输入热量', trigger: 'blur' },
    { type: 'number', message: '热量必须为数字', trigger: 'blur' }
  ]
}

// 加载食物列表
const loadFoods = async () => {
  loading.value = true
  try {
    const res = await getLocalFoods({
      keyword: searchKeyword.value,
      page: page.value,
      page_size: pageSize.value
    })
    
    foods.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该食物吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteLocalFood(row.id)
    ElMessage.success('删除成功')
    loadFoods()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  }
}

// 提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    if (isEdit.value) {
      await updateLocalFood(form.id, form)
      ElMessage.success('编辑成功')
    } else {
      await createLocalFood(form)
      ElMessage.success('新增成功')
    }
    
    dialogVisible.value = false
    loadFoods()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败：' + (error.message || '未知错误'))
    }
  } finally {
    submitting.value = false
  }
}

// 上传成功
const handleUploadSuccess = (response) => {
  form.image_url = response.image_url
  ElMessage.success('图片上传成功')
}

// 上传前校验
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    category: '',
    calories: null,
    protein: 0,
    carbs: 0,
    fat: 0,
    image_url: ''
  })
  formRef.value?.clearValidate()
}

onMounted(() => {
  loadFoods()
})
</script>

<style scoped>
.local-food-library {
  padding: 20px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  max-width: 400px;
}

.food-thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
}

.food-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.calories-text {
  color: #409eff;
  font-weight: 600;
}

.text-muted {
  color: #909399;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}

.food-upload {
  width: 120px;
  height: 120px;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.food-upload:hover {
  border-color: #409eff;
}

.uploaded-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
}
</style>
