<template>
  <div class="app-container">
    <!-- 左侧操作区 -->
    <div class="left-panel">
      <el-card class="upload-card">
        <template #header>
          <div class="panel-header">
            <h2>词云图生成器</h2>
            <el-button type="primary" @click="refreshTasks">
              <el-icon><refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <!-- 统计信息 -->
        <div class="statistics">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="总任务" :value="statistics.total">
                <template #suffix>个</template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="处理中" :value="statistics.processing" value-style="color: #409eff">
                <template #suffix>个</template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="已完成" :value="statistics.completed" value-style="color: #67c23a">
                <template #suffix>个</template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>

        <!-- 上传区域 -->
        <div class="upload-section">
          <el-tabs type="border-card">
            <el-tab-pane label="文件上传" name="upload">
              <el-upload
                class="upload-area"
                drag
                :action="`${API_URL}/api/upload`"
                :on-success="handleSuccess"
                :on-error="handleError"
                :before-upload="beforeUpload"
                :show-file-list="false"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 txt、doc、docx、pdf 格式，不超过 10MB
                  </div>
                </template>
              </el-upload>
            </el-tab-pane>

            <el-tab-pane label="文本输入" name="text">
              <el-input
                v-model="inputText"
                type="textarea"
                :rows="6"
                placeholder="在此��入要生成词云的文本..."
              />
              <el-button 
                type="primary" 
                @click="handleTextSubmit"
                :loading="isSubmitting"
                style="margin-top: 15px; width: 100%"
              >
                生成词云图
              </el-button>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-card>
    </div>

    <!-- 右侧任务列表 -->
    <div class="right-panel">
      <el-card>
        <template #header>
          <div class="panel-header">
            <div class="header-left">
              <h3>任务列表</h3>
              <el-tag>{{ tasks.length }} 个任务</el-tag>
            </div>
            <div class="header-right">
              <el-radio-group v-model="filterStatus" size="small">
                <el-radio-button label="">全部</el-radio-button>
                <el-radio-button label="PENDING">等待中</el-radio-button>
                <el-radio-button label="PROGRESS">处理中</el-radio-button>
                <el-radio-button label="SUCCESS">已完成</el-radio-button>
                <el-radio-button label="FAILURE">失败</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>

        <!-- 任务列表 -->
        <el-table :data="filteredTasks" style="width: 100%">
          <el-table-column label="文件名" prop="filename" min-width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="进度" width="200">
            <template #default="{ row }">
              <el-progress 
                :percentage="row.progress" 
                :status="getProgressStatus(row.status)"
              />
            </template>
          </el-table-column>
          <el-table-column label="预览" width="100">
            <template #default="{ row }">
              <el-image
                v-if="row.imageUrl"
                :src="row.imageUrl"
                :preview-src-list="[row.imageUrl]"
                fit="cover"
                class="preview-image"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><picture-filled /></el-icon>
                  </div>
                </template>
              </el-image>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  v-if="row.imageUrl"
                  type="primary"
                  size="small"
                  @click="downloadImage(row)"
                >
                  <el-icon><download /></el-icon>
                </el-button>
                <el-button
                  v-if="row.status === 'FAILURE'"
                  type="warning"
                  size="small"
                  @click="retryTask(row)"
                >
                  <el-icon><refresh-right /></el-icon>
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteTask(row)"
                >
                  <el-icon><delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  gap: 20px;
  padding: 20px;
  height: calc(100vh - 40px);
  box-sizing: border-box;
  background-color: var(--el-bg-color-page);
}

.left-panel {
  width: 400px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.left-panel .el-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.left-panel :deep(.el-card__body) {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.right-panel .el-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.right-panel :deep(.el-card__body) {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.right-panel .el-table {
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.statistics {
  margin-bottom: 20px;
  padding: 15px;
  background-color: var(--el-bg-color-page);
  border-radius: 4px;
}

.upload-section {
  margin-top: 20px;
}

.preview-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  cursor: pointer;
  z-index: 1;
}

.image-error {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--el-bg-color-page);
  color: var(--el-text-color-secondary);
}

.el-button-group {
  display: flex;
  gap: 5px;
}

:deep(.el-image-viewer__wrapper) {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

:deep(.el-image-viewer__mask) {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9998;
  background-color: rgba(0, 0, 0, 0.9);
}

:deep(.el-image-viewer__close) {
  position: absolute !important;
  top: 40px;
  right: 40px;
  width: 40px;
  height: 40px;
  font-size: 24px;
  color: #fff;
  z-index: 10000;
  cursor: pointer;

  &:hover {
    color: #409EFF;
  }
}

:deep(.el-image-viewer__btn) {
  position: absolute !important;
  z-index: 10000;
  opacity: 0.8;
  cursor: pointer;

  &:hover {
    opacity: 1;
  }
}

:deep(.el-image-viewer__prev) {
  left: 40px;
}

:deep(.el-image-viewer__next) {
  right: 40px;
}

:deep(.el-image-viewer__actions) {
  position: absolute !important;
  left: 50%;
  bottom: 30px;
  transform: translateX(-50%);
  z-index: 10000;
}

:deep(.el-image-viewer__img) {
  z-index: 9999;
}

:deep(.el-tabs__item) {
  color: var(--el-text-color-regular) !important;
  &.is-active {
    color: var(--el-text-color-primary) !important;
    font-weight: bold;
  }
  &:hover {
    color: var(--el-text-color-primary) !important;
  }
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-table__fixed-right) {
  position: static !important;
  box-shadow: none !important;
  background: transparent !important;
}

:deep(.el-table__fixed-right-patch) {
  display: none !important;
}

:deep(.el-button),
:deep(.el-button-group),
:deep(.el-table__fixed-right),
:deep(.cell) {
  position: static !important;
  z-index: 1 !important;
}

:deep(.el-tabs--border-card) {
  border: none;
  box-shadow: none;
  background: transparent;
}

:deep(.el-tabs--border-card > .el-tabs__header) {
  background-color: transparent;
  border: none;
}
</style> 

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL
const inputText = ref('')
const isSubmitting = ref(false)
const filterStatus = ref('')
const tasks = ref([])

// 统计信息
const statistics = computed(() => {
  return {
    total: tasks.value.length,
    processing: tasks.value.filter(t => ['PENDING', 'PROGRESS'].includes(t.status)).length,
    completed: tasks.value.filter(t => t.status === 'SUCCESS').length
  }
})

// 过滤后的任务列表
const filteredTasks = computed(() => {
  if (!filterStatus.value) return tasks.value
  return tasks.value.filter(t => t.status === filterStatus.value)
})

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'SUCCESS': 'success',
    'FAILURE': 'danger',
    'PENDING': 'warning',
    'PROGRESS': 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取进度条状态
const getProgressStatus = (status) => {
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAILURE') return 'exception'
  return ''
}

// 刷新任务列表
const refreshTasks = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/tasks/all`)
    tasks.value = response.data
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  }
}

// 上传前验证
const beforeUpload = (file) => {
  const validTypes = [
    'text/plain',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
  
  if (!validTypes.includes(file.type)) {
    ElMessage.error('只支持 txt、doc、docx、pdf 格式文件！')
    return false
  }
  
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB！')
    return false
  }
  
  return true
}

// 上传成功回调
const handleSuccess = (response) => {
  if (response.task_id) {
    const newTask = {
      taskId: response.task_id,
      filename: response.filename,
      status: 'PENDING',
      progress: 0,
      imageUrl: null
    }
    tasks.value = [...tasks.value, newTask]
    checkTaskStatus(response.task_id)
  } else {
    ElMessage.error('上传失败，请重试')
  }
}

// 上传失败回调
const handleError = () => {
  ElMessage.error('上传失败，请重试')
}

// 检查任务状态
const checkTaskStatus = async (taskId) => {
  try {
    const response = await axios.get(`${API_URL}/api/task/${taskId}`)
    const taskIndex = tasks.value.findIndex(t => t.taskId === taskId)
    if (taskIndex === -1) return

    const task = tasks.value[taskIndex]
    task.status = response.data.status
    
    if (response.data.status === 'SUCCESS') {
      task.imageUrl = `${API_URL}/uploads/${response.data.result.image_path}`
      task.progress = 100
      ElMessage.success(`${task.filename} 的词云图生成成功！`)
    } else if (['PENDING', 'PROGRESS'].includes(response.data.status)) {
      task.progress = response.data.status === 'PROGRESS' ? 50 : 25
      setTimeout(() => checkTaskStatus(taskId), 2000)
    } else if (response.data.status === 'FAILURE') {
      task.progress = 0
      ElMessage.error(`${task.filename} 生成失败：${response.data.error}`)
    }
    tasks.value.splice(taskIndex, 1, task)
  } catch (error) {
    ElMessage.error('检查任务状态失败')
  }
}

// 下载图片
const downloadImage = async (task) => {
  try {
    const response = await axios.get(`${API_URL}/uploads/${task.imageUrl.split('/').pop()}`, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `${task.filename}_wordcloud.png`
    document.body.appendChild(link)
    link.click()
    
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 文本提交处理
const handleTextSubmit = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入文本内容')
    return
  }

  isSubmitting.value = true
  try {
    const blob = new Blob([inputText.value], { type: 'text/plain' })
    const file = new File([blob], 'text.txt', { type: 'text/plain' })
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(`${API_URL}/api/upload`, formData)
    if (response.data.task_id) {
      const newTask = {
        taskId: response.data.task_id,
        filename: response.data.filename,
        status: 'PENDING',
        progress: 0,
        imageUrl: null
      }
      tasks.value = [...tasks.value, newTask]
      checkTaskStatus(response.data.task_id)
      inputText.value = ''  // 清空输入
    }
  } catch (error) {
    ElMessage.error('提交失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// 删除任务
const deleteTask = async (task) => {
  try {
    await axios.delete(`${API_URL}/api/tasks/${task.taskId}`)
    await refreshTasks()
    ElMessage.success('任务已删除')
  } catch (error) {
    ElMessage.error('删除任务失败')
  }
}

// 重试任务
const retryTask = async (task) => {
  try {
    const response = await axios.post(`${API_URL}/api/tasks/${task.taskId}/retry`)
    if (response.data.task_id) {
      await refreshTasks()
      ElMessage.success('任务已重新提交')
    }
  } catch (error) {
    ElMessage.error('重试任务失败')
  }
}

// 初始化时获取任务列表
onMounted(() => {
  refreshTasks()
})
</script> 