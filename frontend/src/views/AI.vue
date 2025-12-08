<template>
  <div class="ai-container">
    <!-- 聊天区域 -->
    <div class="chat-wrapper">
      <!-- 顶部工具栏 -->
      <div class="chat-header">
        <span class="chat-title">AI 助手</span>
        <el-button 
          link 
          size="small" 
          @click="clearChatHistory"
          class="clear-btn"
        >
          🗑️ 清空聊天
        </el-button>
      </div>
      
      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message-item', message.role]"
        >
          <div class="message-avatar">
            <el-avatar
              v-if="message.role === 'assistant'"
              :src="AI_AVATAR"
              :size="40"
            />
            <el-avatar
              v-else
              :src="userStore.userInfo?.avatar || '/default-avatar.png'"
              :size="40"
            />
          </div>
          <div class="message-content">
            <div class="message-bubble">
              <template v-for="part in parseMarkdownCode(message.content)" :key="part">
                <div v-if="part.type === 'text'" class="message-text">{{ part.content }}</div>
                <div v-else-if="part.type === 'code'" class="code-block">
                  <div class="code-header">
                    <span class="code-language">{{ getLanguageDisplayName(part.language) }}</span>
                    <span v-if="!part.isComplete" class="generating-badge">生成中...</span>
                    <el-button 
                      v-else
                      link 
                      size="small" 
                      @click="copyCode(part.content)"
                      class="copy-btn"
                    >
                      📋 复制
                    </el-button>
                  </div>
                  <pre><code :class="'language-' + part.language" v-html="highlightCode(part.content, part.language)"></code></pre>
                </div>
              </template>
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="message-item assistant">
          <div class="message-avatar">
            <el-avatar :src="AI_AVATAR" :size="40" />
          </div>
          <div class="message-content">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-wrapper">
        <div class="input-container">
          <el-input
            v-model="inputValue"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题... (Shift + Enter 换行，Enter 发送)"
            @keydown.enter="handleSendMessage"
            :disabled="loading"
          />
          <el-button
            type="primary"
            :loading="loading"
            @click="handleSendMessage"
            class="send-btn"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import hljs from 'highlight.js/lib/core'
import java from 'highlight.js/lib/languages/java'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import cpp from 'highlight.js/lib/languages/cpp'
import csharp from 'highlight.js/lib/languages/csharp'
import bash from 'highlight.js/lib/languages/bash'
import sql from 'highlight.js/lib/languages/sql'
import 'highlight.js/styles/atom-one-light.css'

// 注册語言
hljs.registerLanguage('java', java)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('csharp', csharp)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sql', sql)

const userStore = useUserStore()
const settingsStore = useSettingsStore()
const messagesContainer = ref(null)
const messages = ref([])
const inputValue = ref('')
const loading = ref(false)

// AI 头像 - 使用本地图片（根据环境自动适配路径）
const AI_AVATAR = import.meta.env.PROD ? '/health/ai-avatar.jpg' : '/ai-avatar.jpg'

// 解析 Markdown 中的代码块（支持流式不完整内容）
const parseMarkdownCode = (content) => {
  // 匹配 ```language\n...\n``` 格式（包括未闭合的代码块）
  const codeBlockRegex = /```([a-zA-Z0-9]*?)\n([\s\S]*?)(?:```|$)/g
  const result = []
  let lastIndex = 0
  let match

  while ((match = codeBlockRegex.exec(content)) !== null) {
    // 添加代码块前的文本
    if (match.index > lastIndex) {
      const textContent = content.slice(lastIndex, match.index)
      if (textContent.trim()) {
        result.push({
          type: 'text',
          content: textContent
        })
      }
    }

    // 检查代码块是否闭合
    const isComplete = match[0].endsWith('```')
    
    // 添加代码块
    result.push({
      type: 'code',
      language: match[1] || 'plaintext',
      content: match[2].trimEnd(),
      isComplete: isComplete  // 标记是否完整
    })

    lastIndex = match.index + match[0].length
  }

  // 添加剩余的文本
  if (lastIndex < content.length) {
    const remainingText = content.slice(lastIndex)
    if (remainingText.trim()) {
      result.push({
        type: 'text',
        content: remainingText
      })
    }
  }

  return result.length > 0 ? result : [{ type: 'text', content }]
}

// 为代码添加基本的语法高亮
const highlightCode = (code, language) => {
  try {
    if (language && hljs.getLanguage(language)) {
      return hljs.highlight(code, { language, ignoreIllegals: true }).value
    }
  } catch (e) {
    console.warn('Code highlight failed:', e)
  }
  return hljs.highlightAuto(code).value
}

// 获取语言的显示名称
const getLanguageDisplayName = (lang) => {
  const names = {
    'javascript': 'JavaScript',
    'typescript': 'TypeScript',
    'python': 'Python',
    'java': 'Java',
    'cpp': 'C++',
    'c': 'C',
    'csharp': 'C#',
    'go': 'Go',
    'rust': 'Rust',
    'php': 'PHP',
    'ruby': 'Ruby',
    'sql': 'SQL',
    'html': 'HTML',
    'css': 'CSS',
    'json': 'JSON',
    'bash': 'Bash',
    'shell': 'Shell',
    'plaintext': 'Code'
  }
  return names[lang.toLowerCase()] || lang.toUpperCase()
}

// 初始化欢迎消息
const initWelcomeMessage = () => {
  // 先尝试从本地存储加载历史消息
  const savedMessages = localStorage.getItem('ai_chat_messages')
  if (savedMessages) {
    try {
      const parsed = JSON.parse(savedMessages)
      // 恢复时间戳对象
      messages.value = parsed.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
      return
    } catch (e) {
      console.error('Failed to load chat history:', e)
    }
  }
  
  // 如果没有历史记录，显示欢迎消息
  messages.value = [
    {
      role: 'assistant',
      content: '你好！👋 我是 AI 助手，可以帮助您解答关于健康管理、饮食、运动等各方面的问题。有什么我可以帮助你的吗？',
      timestamp: new Date()
    }
  ]
}

// 格式化时间
const formatTime = (date) => {
  return dayjs(date).format('HH:mm')
}

// 滚动到最新消息
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 构建系统预设消息（包含用户个人信息）
const buildSystemMessage = () => {
  const userInfo = userStore.userInfo || {}
  const weightUnit = settingsStore.weightUnit || 'kg'
  const unitText = weightUnit === 'jin' ? '斤' : 'kg'
  
  let systemPrompt = '你是一个专业的健康管理助手，专注于帮助用户进行体重管理、饮食规划和运动指导。'
  
  // 添加单位说明
  systemPrompt += `\n\n重要提示：用户使用的体重单位是 ${unitText}，所有关于体重的回答都应该使用 ${unitText} 作为单位。`
  
  // 添加用户基本信息
  if (userInfo.nickname || userInfo.phone) {
    systemPrompt += `\n\n当前用户信息：`
    systemPrompt += `\n- 用户名：${userInfo.nickname || userInfo.phone}`
    
    if (userInfo.gender) {
      const genderText = userInfo.gender === 'male' ? '男' : userInfo.gender === 'female' ? '女' : '其他'
      systemPrompt += `\n- 性别：${genderText}`
    }
    
    if (userInfo.age) {
      systemPrompt += `\n- 年龄：${userInfo.age}岁`
    }
    
    if (userInfo.height) {
      systemPrompt += `\n- 身高：${userInfo.height}cm`
    }
    
    if (userInfo.current_weight) {
      const displayWeight = settingsStore.convertWeightToDisplay(userInfo.current_weight)
      systemPrompt += `\n- 当前体重：${displayWeight}${unitText}`
    }
    
    if (userInfo.target_weight) {
      const displayTargetWeight = settingsStore.convertWeightToDisplay(userInfo.target_weight)
      systemPrompt += `\n- 目标体重：${displayTargetWeight}${unitText}`
    }
    
    // 计算 BMI
    if (userInfo.height && userInfo.current_weight) {
      const heightInMeters = userInfo.height / 100
      const bmi = (userInfo.current_weight / (heightInMeters * heightInMeters)).toFixed(1)
      systemPrompt += `\n- BMI：${bmi}`
      
      // BMI 分析
      if (bmi < 18.5) {
        systemPrompt += ' (偏瘦)'
      } else if (bmi < 24) {
        systemPrompt += ' (正常)'
      } else if (bmi < 28) {
        systemPrompt += ' (超重)'
      } else {
        systemPrompt += ' (肥胖)'
      }
    }
    
    // 添加目标说明
    if (userInfo.target_weight && userInfo.current_weight) {
      const diff = userInfo.current_weight - userInfo.target_weight
      const displayDiff = settingsStore.convertWeightToDisplay(Math.abs(diff))
      if (diff > 0) {
        systemPrompt += `\n- 减重目标：需要减重${displayDiff}${unitText}`
      } else if (diff < 0) {
        systemPrompt += `\n- 增重目标：需要增重${displayDiff}${unitText}`
      } else {
        systemPrompt += `\n- 已达到目标体重`
      }
    }
  }
  
  systemPrompt += '\n\n请根据以上用户信息，提供个性化的健康建议和指导。回答要专业、友好、实用。记住，所有涉及体重的数值都使用 ' + unitText + ' 作为单位。'
  
  return {
    role: 'system',
    content: systemPrompt
  }
}

// 发送消息
const handleSendMessage = async (event) => {
  // 如果是 Shift + Enter，则换行；否则发送消息
  if (event && event.shiftKey) {
    return
  }

  if (event && event.type === 'keydown') {
    event.preventDefault()
  }

  const message = inputValue.value.trim()
  if (!message || loading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })

  inputValue.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    // 构建系统预设消息（包含用户信息）
    const systemMessage = buildSystemMessage()
    
    // 调用后端 API
    const response = await fetch('/health/api/v1/ai/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          systemMessage,  // 添加系统预设消息
          ...messages.value
            .filter(m => m.role !== 'thinking')
            .map(m => ({
              role: m.role,
              content: m.content
            }))
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    })

    if (!response.ok) {
      throw new Error('API 请求失败')
    }

    // 处理流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let assistantMessage = {
      role: 'assistant',
      content: '',
      timestamp: new Date()
    }

    messages.value.push(assistantMessage)
    await scrollToBottom()

    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      
      // 保留最后一行（可能不完整）
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (trimmed.startsWith('data: ')) {
          try {
            const dataStr = trimmed.slice(6)
            if (dataStr === '[DONE]') {
              continue
            }
            const json = JSON.parse(dataStr)
            if (json.choices?.[0]?.delta?.content) {
              assistantMessage.content += json.choices[0].delta.content
              // 强制更新消息以触发界面重新渲染
              messages.value[messages.value.length - 1] = { ...assistantMessage }
              await scrollToBottom()
            }
          } catch (e) {
            // 忽略解析错误
            console.error('Error parsing SSE:', e)
          }
        }
      }
    }
    
    // 处理缓冲区中剩余的数据
    if (buffer.trim()) {
      const trimmed = buffer.trim()
      if (trimmed.startsWith('data: ')) {
        try {
          const dataStr = trimmed.slice(6)
          if (dataStr !== '[DONE]') {
            const json = JSON.parse(dataStr)
            if (json.choices?.[0]?.delta?.content) {
              assistantMessage.content += json.choices[0].delta.content
              messages.value[messages.value.length - 1] = { ...assistantMessage }
            }
          }
        } catch (e) {
          console.error('Error parsing final SSE:', e)
        }
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请重试')
    // 移除加载消息
    messages.value.pop()
  } finally {
    loading.value = false
    await scrollToBottom()
    // 保存聊天记录到本地存储
    saveChatHistory()
  }
}

// 保存聊天记录到本地存储
const saveChatHistory = () => {
  try {
    localStorage.setItem('ai_chat_messages', JSON.stringify(messages.value))
  } catch (e) {
    console.error('Failed to save chat history:', e)
  }
}

// 清空聊天记录
const clearChatHistory = () => {
  messages.value = []
  localStorage.removeItem('ai_chat_messages')
  initWelcomeMessage()
}

onMounted(() => {
  // 加载用户信息和设置
  loadUserData()
  initWelcomeMessage()
  scrollToBottom()
})

// 加载用户数据
const loadUserData = async () => {
  try {
    await userStore.fetchUserInfo()
    await settingsStore.loadSettings()
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
}

// 复制代码到剪贴板
const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请重试')
  })
}
</script>

<style scoped>
.ai-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.chat-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  background: #fff;
}

.chat-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.clear-btn {
  color: #999;
  --el-link-text-color: #999;
}

.clear-btn:hover {
  color: #f56c6c;
  --el-link-text-color: #f56c6c;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f5f7fa;
}

.message-item {
  display: flex;
  gap: 12px;
  animation: slideIn 0.3s ease-out;
}

.message-item.user {
  flex-direction: row-reverse;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-bubble {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-item.assistant .message-bubble {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 12px 16px;
}

.message-item.user .message-bubble {
  background: #409eff;
  border-radius: 12px;
  padding: 12px 16px;
}

.message-item.assistant .message-content {
  align-items: flex-start;
}

.message-item.user .message-content {
  align-items: flex-end;
}

.message-text {
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 14px;
  color: inherit;
}

.message-item.assistant .message-text {
  color: #333;
}

.message-item.user .message-text {
  color: #fff;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  padding: 0 4px;
}

.chat-input-wrapper {
  border-top: 1px solid #e0e0e0;
  padding: 20px;
  background: #fff;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-container :deep(.el-textarea) {
  flex: 1;
}

.input-container :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: none;
}

.send-btn {
  padding: 0 32px;
}

/* 加载动画 */
.loading-dots {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: bounce 1.4s infinite;
}

.loading-dots span:nth-child(1) {
  animation-delay: 0s;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 代码块样式 */
.code-block {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  font-size: 13px;
  max-width: 100%;
}

.message-item.user .code-block {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #ececec;
  border-bottom: 1px solid #e0e0e0;
}

.code-language {
  color: #666;
  font-weight: 500;
  font-size: 12px;
}

.generating-badge {
  color: #409eff;
  font-size: 12px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.copy-btn {
  color: #999;
  padding: 0 4px;
  --el-link-text-color: #999;
}

.copy-btn:hover {
  color: #333;
  --el-link-text-color: #333;
}

.code-block pre {
  margin: 0;
  padding: 12px;
  overflow-x: auto;
}

.code-block code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  line-height: 1.6;
  background: transparent;
  padding: 0;
}

/* 代码高亮样式 - 使用 highlight.js atom-one-light 主题 */
.code-block .hljs {
  background: transparent;
  padding: 0;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>
