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

      <!-- 处理状态 -->
      <div v-if="taskId" class="status-area">
        <el-progress
          v-if="['PENDING', 'PROGRESS'].includes(status)"
          type="circle"
          :percentage="50"
          status="warning"
        />
        <div class="status-text">{{ statusMessage }}</div>
      </div>

      <!-- 结果展示 -->
      <div v-if="wordcloudUrl" class="result-area">
        <el-image
          :src="wordcloudUrl"
          fit="contain"
          class="wordcloud-image"
          :preview-src-list="[wordcloudUrl]"
        />
        <el-button type="primary" @click="downloadImage">
          <el-icon><download /></el-icon>
          下载词云图
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL
const taskId = ref('')
const status = ref('')
const wordcloudUrl = ref('')

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
    taskId.value = response.task_id
    status.value = 'PENDING'
    checkTaskStatus()
  } else {
    ElMessage.error('上传失败，请重试')
  }
}

// 上传失败回调
const handleError = () => {
  ElMessage.error('上传失败，请重试')
}

// 检查任务状态
const checkTaskStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/task/${taskId.value}`)
    status.value = response.data.status
    
    if (response.data.status === 'SUCCESS') {
      wordcloudUrl.value = `${API_URL}/uploads/${response.data.result.image_path}`
      ElMessage.success('词云图生成成功！')
    } else if (['PENDING', 'PROGRESS'].includes(response.data.status)) {
      setTimeout(checkTaskStatus, 2000) // 这里设置了2秒后重新检查
    } else if (response.data.status === 'FAILURE') {
      ElMessage.error('生成失败，请重试')
    }
  } catch (error) {
    ElMessage.error('检查任务状态失败')
  }
}

// 下载图片
const downloadImage = async () => {
  try {
    // 使用 axios 获取图片数据
    const response = await axios.get(`${API_URL}/uploads/${wordcloudUrl.value.split('/').pop()}`, {
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
</style> 