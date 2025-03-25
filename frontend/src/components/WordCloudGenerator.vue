
<template>
  <div class="app-container">
    <el-row :gutter="20">
      <!-- 左侧操作区 -->
      <el-col :xs="24" :sm="24" :md="10" :lg="8" :xl="6">
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
                <el-col :xs="8" :sm="8">
                  <el-statistic title="总任务" :value="statistics.total">
                    <template #suffix>个</template>
                  </el-statistic>
                </el-col>
                <el-col :xs="8" :sm="8">
                  <el-statistic title="处理中" :value="statistics.processing" value-style="color: #409eff">
                    <template #suffix>个</template>
                  </el-statistic>
                </el-col>
                <el-col :xs="8" :sm="8">
                  <el-statistic title="已完成" :value="statistics.completed" value-style="color: #67c23a">
                    <template #suffix>个</template>
                  </el-statistic>
                </el-col>
              </el-row>
            </div>

            <!-- 停用词输入 -->
            <el-form-item label="要忽略的词">
              <el-input
                v-model="stopWords"
                type="text"
                placeholder="输入要忽略的词，用英文逗号分隔"
              />
            </el-form-item>

            <!-- 上传区域 -->
            <div class="upload-section">
              <el-tabs v-model="activeTab" type="border-card">
                <el-tab-pane label="文件上传" name="upload">
                  <el-upload
                    class="upload-area"
                    drag
                    :action="`${API_URL}/api/upload`"
                    :on-success="handleUploadSuccess"
                    :on-error="handleError"
                    :before-upload="beforeUpload"
                    :show-file-list="false"
                    :http-request="customUpload"
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
                    placeholder="在此输入要生成词云的文本..."
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
      </el-col>

      <!-- 右侧任务列表 -->
      <el-col :xs="24" :sm="24" :md="14" :lg="16" :xl="18">
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
            <div class="table-responsive">
              <el-table :data="filteredTasks" style="width: 100%">
                <el-table-column 
                  label="文件名" 
                  prop="filename" 
                  min-width="120"
                  show-overflow-tooltip 
                />
                <el-table-column 
                  label="状态" 
                  :width="isMobile ? 80 : 100"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column 
                  label="停用词" 
                  min-width="150"
                  show-overflow-tooltip
                >
                  <template #default="{ row }">
                    <span v-if="row.stopWords">{{ row.stopWords }}</span>
                    <span v-else class="text-gray">无</span>
                  </template>
                </el-table-column>
                <el-table-column 
                  label="进度" 
                  :width="isMobile ? 120 : 200"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-progress 
                      :percentage="row.progress" 
                      :status="getProgressStatus(row.status)"
                    >
                      <template #default="{ percentage }">
                        <span>{{ percentage }}% {{ row.step || '' }}</span>
                      </template>
                    </el-progress>
                  </template>
                </el-table-column>
                <el-table-column 
                  label="预览" 
                  :width="isMobile ? 60 : 100"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-image
                      v-if="row.imageUrl"
                      :src="row.imageUrl"
                      :preview-src-list="[row.imageUrl]"
                      :initial-index="0"
                      fit="cover"
                      :preview-teleported="true"
                      class="preview-image"
                      :class="{ 'mobile-preview': isMobile }"
                    >
                      <template #error>
                        <div class="image-error">
                          <el-icon><picture-filled /></el-icon>
                        </div>
                      </template>
                    </el-image>
                  </template>
                </el-table-column>
                <el-table-column 
                  label="操作" 
                  :width="isMobile ? 120 : 200"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-space :size="isMobile ? 4 : 10">
                      <el-button
                        v-if="row.imageUrl"
                        type="primary"
                        :size="isMobile ? 'small' : 'default'"
                        @click="downloadImage(row)"
                      >
                        <el-icon><download /></el-icon>
                      </el-button>
                      <el-button
                        v-if="row.status === 'FAILURE'"
                        type="warning"
                        :size="isMobile ? 'small' : 'default'"
                        @click="retryTask(row)"
                      >
                        <el-icon><refresh-right /></el-icon>
                      </el-button>
                      <el-button
                        type="danger"
                        :size="isMobile ? 'small' : 'default'"
                        @click="deleteTask(row)"
                      >
                        <el-icon><delete /></el-icon>
                      </el-button>
                    </el-space>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL
const activeTab = ref('upload')
const inputText = ref('')
const stopWords = ref('')  // 停用词输入
const isSubmitting = ref(false)
const filterStatus = ref('')
const tasks = ref([])

// 监听tasks变化，自动保存到localStorage
watch(tasks, (newTasks) => {
  localStorage.setItem('wordcloud_tasks', JSON.stringify(newTasks))
}, { deep: true })

// 检测是否为移动设备
const isMobile = computed(() => {
  return window.innerWidth <= 768
})

// 监听窗口大小变化
window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth <= 768
})

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

// 初始化时获取任务列表
onMounted(() => {
  const savedTasks = localStorage.getItem('wordcloud_tasks')
  if (savedTasks) {
    tasks.value = JSON.parse(savedTasks)
    // 对于未完成的任务，继续检查状态
    tasks.value.forEach(task => {
      if (['PENDING', 'PROGRESS'].includes(task.status)) {
        checkTaskStatus(task.taskId)
      }
    })
  }
})

// 上传前验证
const beforeUpload = (file) => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB！')
    return false
  }
  
  return true
}

// 自定义上传函数
const customUpload = async (options) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    formData.append('stop_words', stopWords.value)

    const response = await axios.post(`${API_URL}/api/upload`, formData)
    options.onSuccess(response.data)
  } catch (error) {
    options.onError(error)
  }
}

// 上传成功回调
const handleUploadSuccess = (response) => {
  if (response.task_id) {
    const newTask = {
      taskId: response.task_id,
      filename: response.filename,
      status: 'PENDING',
      progress: 0,
      imageUrl: null,
      step: '',
      stopWords: stopWords.value
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
    task.progress = response.data.progress || 0
    task.step = response.data.step
    
    if (response.data.status === 'SUCCESS') {
      task.imageUrl = `${API_URL}/uploads/${response.data.result.image_path}`
      task.progress = 100
      ElMessage.success(`${task.filename} 的词云图生成成功！`)
    } else if (['PENDING', 'PROGRESS'].includes(response.data.status)) {
      setTimeout(() => checkTaskStatus(taskId), 500)
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
    // 使用带时间戳的文件名，去掉文本文件的后缀
    console.log('task.filename', task.filename)
    const fileNameWithoutExt = task.filename.replace(/\.[^.]+$/, '')
    link.download = `${fileNameWithoutExt}.png`
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
    const timestamp = new Date().getTime()
    const blob = new Blob([inputText.value], { type: 'text/plain' })
    // const file = new File([blob], `text_${timestamp}.txt`, { type: 'text/plain' })
    const file = new File([blob], `text.txt`, { type: 'text/plain' })
    const formData = new FormData()
    formData.append('file', file)
    formData.append('stop_words', stopWords.value)

    const response = await axios.post(`${API_URL}/api/upload`, formData)
    if (response.data.task_id) {
      const newTask = {
        taskId: response.data.task_id,
        filename: response.data.filename,
        status: 'PENDING',
        progress: 0,
        imageUrl: null,
        step: ''
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
    if (!task.taskId) {
      ElMessage.error('任务ID不存在')
      return
    }
    
    await axios.delete(`${API_URL}/api/tasks/${task.taskId}`)
    tasks.value = tasks.value.filter(t => t.taskId !== task.taskId)
    ElMessage.success('任务已删除')
  } catch (error) {
    console.error('Delete task error:', error)
    ElMessage.error('删除任务失败')
  }
}

// 重试任务
const retryTask = async (task) => {
  try {
    const response = await axios.post(`${API_URL}/api/tasks/${task.taskId}/retry`)
    if (response.data.task_id) {
      tasks.value = tasks.value.map(t => {
        if (t.taskId === task.taskId) {
          return {
            ...t,
            status: 'PENDING',
            progress: 0,
            step: ''
          }
        }
        return t
      })
      checkTaskStatus(task.taskId)
      ElMessage.success('任务已重新提交')
    }
  } catch (error) {
    ElMessage.error('重试任务失败')
  }
}
</script>

<style scoped>
.text-gray {
  color: #909399;
  font-style: italic;
}

.app-container {
  padding: var(--el-main-padding);
  min-height: calc(100vh - var(--el-main-padding) * 2);
  background-color: var(--el-bg-color-page);
}

.left-panel,
.right-panel {
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-right .el-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.statistics {
  margin-bottom: 20px;
  padding: 15px;
  background-color: var(--el-bg-color-page);
  border-radius: var(--el-border-radius-base);
}

.upload-section {
  margin-top: 20px;
}

.preview-image {
  width: 50px;
  height: 50px;
  border-radius: var(--el-border-radius-base);
  cursor: pointer;
}

.mobile-preview {
  width: 40px;
  height: 40px;
}

.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--el-bg-color-page);
  color: var(--el-text-color-secondary);
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .app-container {
    padding: 10px;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    overflow-x: auto;
  }

  .el-radio-group {
    padding-bottom: 5px;
  }

  .statistics {
    padding: 10px;
  }

  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-button) {
    padding: 6px;
  }
}

/* 图片预览样式 */
:deep(.el-overlay) {
  .el-image-viewer__wrapper {
    position: fixed;
    inset: 0;
    z-index: 2100;
  }

  .el-image-viewer__mask {
    position: fixed;
    inset: 0;
    z-index: 2099;
    background-color: rgba(0, 0, 0, 0.9);
  }

  .el-image-viewer__btn {
    position: absolute;
    z-index: 2101;
  }

  .el-image-viewer__close {
    top: 40px;
    right: 40px;
    z-index: 2102;
  }

  .el-image-viewer__canvas {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 2101;
  }

  .el-image-viewer__actions {
    position: absolute;
    left: 50%;
    bottom: 30px;
    transform: translateX(-50%);
    z-index: 2102;
  }
}

/* 优化表格在移动端的显示 */
:deep(.el-table__header) {
  th {
    padding: 8px 0;
  }
}

:deep(.el-table__body) {
  td {
    padding: 8px 0;
  }
}
</style>