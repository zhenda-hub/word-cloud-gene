<template>
  <div class="upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <h2>词云图生成器</h2>
        </div>
      </template>

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
            支持 txt、doc、docx、pdf 格式文件，大小不超过 10MB
          </div>
        </template>
      </el-upload>

      <!-- 添加文本输入区域 -->
      <div class="text-input-area">
        <el-divider>或者直接输入文本</el-divider>
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
          style="margin-top: 15px"
        >
          生成词云图
        </el-button>
      </div>

      <!-- 处理状态 -->
      <div v-if="currentTasks.length" class="results-grid">
        <el-card v-for="task in currentTasks" :key="task.taskId" class="result-card">
          <template #header>
            <div class="result-header">
              <span>{{ task.filename }}</span>
              <el-tag :type="getStatusType(task.status)">{{ task.status }}</el-tag>
            </div>
          </template>
          
          <!-- 加载中状态 -->
          <div v-if="['PENDING', 'PROGRESS'].includes(task.status)" class="loading-state">
            <el-progress type="circle" :percentage="50" status="warning" />
            <div class="status-text">{{ statusMessage }}</div>
          </div>

          <!-- 结果展示 -->
          <div v-else-if="task.imageUrl" class="result-content">
            <el-image
              :src="task.imageUrl"
              fit="contain"
              class="wordcloud-image"
              :preview-src-list="[task.imageUrl]"
            />
            <el-button type="primary" size="small" @click="downloadImage(task)">
              <el-icon><download /></el-icon>
              下载词云图
            </el-button>
          </div>

          <!-- 失败状态 -->
          <div v-else-if="task.status === 'FAILURE'" class="error-state">
            <el-icon><circle-close /></el-icon>
            <span>生成失败</span>
          </div>
        </el-card>
      </div>

      <!-- 添加任务管理面板 -->
      <el-divider>任务管理</el-divider>
      <div class="task-panel">
        <el-tabs>
          <el-tab-pane label="当前任务">
            <el-button @click="refreshTaskInfo" size="small">
              <el-icon><refresh /></el-icon>
              刷新
            </el-button>
            <el-descriptions v-if="taskInfo" border>
              <el-descriptions-item label="活动任务">
                {{ taskInfo.active ? Object.keys(taskInfo.active).length : 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="等待任务">
                {{ taskInfo.reserved ? Object.keys(taskInfo.reserved).length : 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="计划任务">
                {{ taskInfo.scheduled ? Object.keys(taskInfo.scheduled).length : 0 }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="历史任务">
            <el-button @click="refreshHistoryTasks" size="small">
              <el-icon><refresh /></el-icon>
              刷新
            </el-button>
            <el-table :data="historyTasks" style="width: 100%" v-if="historyTasks.length">
              <el-table-column prop="task_id" label="任务ID" width="220" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="date_done" label="完成时间" />
            </el-table>
            <el-empty v-else description="暂无历史任务" />
          </el-tab-pane>

          <el-tab-pane label="Redis信息">
            <el-button @click="refreshRedisInfo" size="small">
              <el-icon><refresh /></el-icon>
              刷新
            </el-button>
            <el-descriptions v-if="redisInfo" border direction="vertical">
              <el-descriptions-item label="键总数">
                {{ Object.keys(redisInfo.keys).length }}
              </el-descriptions-item>
              <el-descriptions-item label="任务总数">
                {{ Object.keys(redisInfo.tasks).length }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled, Download, Refresh, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL
const inputText = ref('')
const isSubmitting = ref(false)

// 修改状态管理
const tasks = ref(new Map()) // 存储所有任务状态：Map<taskId, {status, filename, imageUrl}>
const currentTasks = computed(() => Array.from(tasks.value.values()))

// 状态信息映射
const statusMessage = computed(() => {
  const statusMap = {
    'PENDING': '正在处理文件...',
    'PROGRESS': '生成词云图中...',
    'SUCCESS': '生成完成！',
    'FAILURE': '生成失败，请重试'
  }
  return statusMap[status.value] || '准备就绪'
})

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
    tasks.value.set(response.task_id, {
      taskId: response.task_id,
      filename: response.filename,
      status: 'PENDING',
      imageUrl: null
    })
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
    const task = tasks.value.get(taskId)
    if (!task) return

    task.status = response.data.status
    
    if (response.data.status === 'SUCCESS') {
      task.imageUrl = `${API_URL}/uploads/${response.data.result.image_path}`
      ElMessage.success(`${task.filename} 的词云图生成成功！`)
    } else if (['PENDING', 'PROGRESS'].includes(response.data.status)) {
      setTimeout(() => checkTaskStatus(taskId), 2000)
    } else if (response.data.status === 'FAILURE') {
      ElMessage.error(`${task.filename} 生成失败：${response.data.error}`)
    }
    tasks.value.set(taskId, task)
  } catch (error) {
    ElMessage.error('检查任务状态失败')
  }
}

// 下载图片
const downloadImage = async (task) => {
  try {
    // 使用 axios 获取图片数据
    const response = await axios.get(`${API_URL}/uploads/${task.imageUrl.split('/').pop()}`, {
      responseType: 'blob'  // 重要：指定响应类型为 blob
    })
    
    // 创建 Blob URL
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    
    // 创建临时下载链接
    const link = document.createElement('a')
    link.href = url
    link.download = 'wordcloud.png'  // 设置下载文件名
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 处理文本提交
const handleTextSubmit = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入文本内容')
    return
  }

  isSubmitting.value = true
  try {
    // 将文本内容作为文件上传
    const blob = new Blob([inputText.value], { type: 'text/plain' })
    const file = new File([blob], 'text.txt', { type: 'text/plain' })
    
    // 创建 FormData
    const formData = new FormData()
    formData.append('file', file)

    // 发送请求
    const response = await axios.post(`${API_URL}/api/upload`, formData)
    
    if (response.data.task_id) {
      tasks.value.set(response.data.task_id, {
        taskId: response.data.task_id,
        filename: response.data.filename,
        status: 'PENDING',
        imageUrl: null
      })
      checkTaskStatus(response.data.task_id)
    } else {
      ElMessage.error('上传失败，请重试')
    }
  } catch (error) {
    ElMessage.error('提交失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// 添加新的响应式变量
const taskInfo = ref(null)
const historyTasks = ref([])
const redisInfo = ref(null)

// 刷新当前任务信息
const refreshTaskInfo = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/tasks/inspect`)
    taskInfo.value = response.data
  } catch (error) {
    ElMessage.error('获取任务信息失败')
  }
}

// 刷新历史任务
const refreshHistoryTasks = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/tasks/all`)
    historyTasks.value = response.data
  } catch (error) {
    ElMessage.error('获取历史任务失败')
  }
}

// 刷新Redis信息
const refreshRedisInfo = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/redis/info`)
    redisInfo.value = response.data
  } catch (error) {
    ElMessage.error('获取Redis信息失败')
  }
}

// 获取状态标签类型
const getStatusType = (status) => {
  const typeMap = {
    'SUCCESS': 'success',
    'FAILURE': 'danger',
    'PENDING': 'warning',
    'PROGRESS': 'warning'
  }
  return typeMap[status] || 'info'
}
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.card-header {
  text-align: center;
}

.upload-area {
  width: 100%;
}

.status-area {
  margin-top: 20px;
  text-align: center;
}

.status-text {
  margin-top: 10px;
  color: #666;
}

.result-area {
  margin-top: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.wordcloud-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.text-input-area {
  margin-top: 20px;
  width: 100%;
}

.el-divider {
  margin: 24px 0;
}

.task-panel {
  margin-top: 20px;
}

.el-button {
  margin-bottom: 15px;
}

.el-descriptions {
  margin-top: 15px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.result-card {
  height: 100%;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 10px;
}

.error-state {
  color: var(--el-color-danger);
}
</style> 