<template>
  <div class="ai-container">
    <!-- 聊天区域 -->
    <div class="chat-wrapper">
      <!-- 顶部工具栏 -->
      <div class="chat-header">
        <span class="chat-title">AI 助手</span>
        <div class="header-actions">
          <!-- 模型切换 -->
          <el-radio-group v-model="aiProvider" size="small" class="model-switch">
            <el-radio-button label="openai">
              <span class="model-label">🤖 ChatGPT</span>
            </el-radio-button>
            <el-radio-button label="gemini">
              <span class="model-label">🤖 Gemini</span>
            </el-radio-button>
          </el-radio-group>
          <el-button 
            link 
            size="small" 
            @click="clearChatHistory"
            class="clear-btn"
          >
            🗑️ 清空聊天
          </el-button>
        </div>
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
            <!-- 如果是助手消息，显示模型名称 -->
            <div v-if="message.role === 'assistant'" class="model-name">
              <svg class="model-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="currentColor"/>
                <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" fill="currentColor" opacity="0.6"/>
              </svg>
              <span>{{ currentModel }}</span>
            </div>
            <div class="message-bubble">
              <!-- 如果是助手消息，且内容为空，显示加载动画 -->
              <div v-if="message.role === 'assistant' && !message.content" class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <!-- 如果是助手消息且有内容，使用 Markdown 渲染 -->
              <div 
                v-else-if="message.role === 'assistant'" 
                class="markdown-content"
                v-html="renderMarkdown(message.content)"
              ></div>
              <!-- 用户消息直接显示 -->
              <div v-else class="message-text">{{ message.content }}</div>
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
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
            @click="loading ? stopGeneration() : handleSendMessage()"
            class="send-btn"
          >
            {{ loading ? '⏸ 停止' : '✉️ 发送' }}
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
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import java from 'highlight.js/lib/languages/java'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import cpp from 'highlight.js/lib/languages/cpp'
import csharp from 'highlight.js/lib/languages/csharp'
import bash from 'highlight.js/lib/languages/bash'
import sql from 'highlight.js/lib/languages/sql'
import 'highlight.js/styles/atom-one-light.css'

// 注册语言
hljs.registerLanguage('java', java)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('csharp', csharp)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sql', sql)

// 配置 marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (e) {
        console.error('Highlight error:', e)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,  // 支持 GFM 换行
  gfm: true      // 启用 GitHub Flavored Markdown
})

const userStore = useUserStore()
const settingsStore = useSettingsStore()
const messagesContainer = ref(null)
const messages = ref([])
const inputValue = ref('')
const loading = ref(false)

// 用于中止请求的 AbortController
let abortController = null

// AI 服务提供商（默认使用 ChatGPT）
const aiProvider = ref('openai')

// 模型配置
const modelConfig = {
  gemini: 'gemini-2.0-flash',
  openai: 'gpt-4o-mini'
}

// 获取当前模型名称
const currentModel = computed(() => modelConfig[aiProvider.value])

// AI 头像 - 使用本地图片（根据环境自动适配路径）
const AI_AVATAR = import.meta.env.PROD ? '/health/ai-avatar.jpg' : '/ai-avatar.jpg'

// 渲染 Markdown 内容（处理列表层级）
const renderMarkdown = (content) => {
  try {
    let html = marked.parse(content)
    // 处理嵌套列表，添加层级样式
    html = processNestedLists(html)
    // 手动高亮代码块（因为 processNestedLists 可能破坏了 marked 的高亮）
    html = highlightCodeBlocks(html)
    return html
  } catch (e) {
    console.error('Markdown parse error:', e)
    return content
  }
}

// 手动高亮代码块
const highlightCodeBlocks = (html) => {
  const div = document.createElement('div')
  div.innerHTML = html
  
  // 查找所有代码块
  const codeBlocks = div.querySelectorAll('pre code')
  codeBlocks.forEach(block => {
    // 获取语言
    const className = block.className
    const langMatch = className.match(/language-(\w+)/)
    const lang = langMatch ? langMatch[1] : ''
    
    // 获取代码内容
    const code = block.textContent
    
    // 使用 highlight.js 高亮
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlighted = hljs.highlight(code, { language: lang })
        block.innerHTML = highlighted.value
        block.classList.add('hljs')
      } catch (e) {
        console.error('Highlight error:', e)
      }
    } else {
      // 自动检测语言
      try {
        const highlighted = hljs.highlightAuto(code)
        block.innerHTML = highlighted.value
        block.classList.add('hljs')
      } catch (e) {
        console.error('Auto highlight error:', e)
      }
    }
  })
  
  return div.innerHTML
}

// 处理嵌套列表，添加层级样式
const processNestedLists = (html) => {
  // 创建一个临时 DOM 来处理
  const div = document.createElement('div')
  div.innerHTML = html
  
  // 获取所有列表项
  const allItems = div.querySelectorAll('li')
  
  allItems.forEach(item => {
    // 计算嵌套层级
    let level = 1
    let parent = item.parentElement
    while (parent && parent !== div) {
      if (parent.tagName === 'UL' || parent.tagName === 'OL') {
        // 检查父元素是否在另一个 li 内
        if (parent.parentElement && parent.parentElement.tagName === 'LI') {
          level++
        }
      }
      parent = parent.parentElement
    }
    
    item.classList.add(`md-item-level-${level}`)
  })
  
  return div.innerHTML
}

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
  
  // 创建新的 AbortController
  abortController = new AbortController()
  
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
        model: modelConfig[aiProvider.value],
        provider: aiProvider.value,
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
      }),
      signal: abortController.signal  // 添加 abort signal
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
    let lastUpdateTime = Date.now()
    const UPDATE_INTERVAL = 50 // 每50ms更新一次界面，减少渲染频率
    
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
              
              // 使用时间间隔控制更新频率，减少渲染次数
              const now = Date.now()
              if (now - lastUpdateTime > UPDATE_INTERVAL) {
                // 强制更新消息以触发界面重新渲染
                messages.value[messages.value.length - 1] = { ...assistantMessage }
                await scrollToBottom()
                lastUpdateTime = now
              }
            }
          } catch (e) {
            // 忽略解析错误
            console.error('Error parsing SSE:', e)
          }
        }
      }
    }
    
    // 最后强制更新一次，确保显示完整内容
    messages.value[messages.value.length - 1] = { ...assistantMessage }
    
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
    
    // 如果是用户主动中止，不显示错误提示
    if (error.name === 'AbortError') {
      ElMessage.info('已停止生成')
      // 如果最后一条消息是空的助手消息，则移除它
      if (messages.value.length > 0 && 
          messages.value[messages.value.length - 1].role === 'assistant' && 
          !messages.value[messages.value.length - 1].content) {
        messages.value.pop()
      }
    } else {
      ElMessage.error('发送消息失败，请重试')
      // 移除加载消息
      messages.value.pop()
    }
  } finally {
    loading.value = false
    abortController = null  // 清理 AbortController
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

// 停止生成
const stopGeneration = () => {
  if (abortController) {
    abortController.abort()
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.model-switch {
  --el-radio-button-checked-bg-color: #409eff;
  --el-radio-button-checked-border-color: #409eff;
}

.model-label {
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
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

.model-name {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.model-icon {
  width: 16px;
  height: 16px;
  color: #666;
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
  padding: 12px 16px 12px 24px;  /* 左侧增加到 24px，为列表符号预留空间 */
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

/* Markdown 内容样式 */
.markdown-content {
  line-height: 1.6;
  color: #333;
  word-wrap: break-word;
  font-size: 14px;
  padding: 4px 0 4px 8px;  /* 左侧预留 8px 给列表符号 */
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  margin: 16px 0 8px;
  font-weight: 600;
  line-height: 1.4;
}

.markdown-content :deep(h1) {
  font-size: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 8px;
}

.markdown-content :deep(h2) {
  font-size: 18px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 6px;
}

.markdown-content :deep(h3) {
  font-size: 16px;
}

.markdown-content :deep(p) {
  margin: 8px 0;
}

/* 列表样式优化 - 使用 :deep() 穿透 scoped */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 0;
  list-style: none;
}

.markdown-content :deep(li) {
  position: relative;
  margin: 6px 0;
}

/* 一级列表 */
.markdown-content :deep(.md-item-level-1) {
  padding-left: 20px;
}

.markdown-content :deep(.md-item-level-1)::before {
  content: '•';
  position: absolute;
  left: 4px;
  color: #333;
  font-weight: bold;
}

/* 二级列表 */
.markdown-content :deep(.md-item-level-2) {
  padding-left: 40px;
}

.markdown-content :deep(.md-item-level-2)::before {
  content: '◦';
  position: absolute;
  left: 24px;
  color: #666;
}

/* 三级列表 */
.markdown-content :deep(.md-item-level-3) {
  padding-left: 60px;
}

.markdown-content :deep(.md-item-level-3)::before {
  content: '▪';
  position: absolute;
  left: 44px;
  color: #999;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #333;
}

.markdown-content :deep(em) {
  font-style: italic;
}

/* 行内代码样式 - 只应用于非代码块内的 code */
.markdown-content :deep(:not(pre) > code) {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  color: #d73a49;  /* GitHub 风格的红色 */
  border: 1px solid #e1e4e8;
}

/* 代码块样式 */
.markdown-content :deep(pre) {
  background: #f6f8fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 12px 0;
}

/* 代码块内的 code - 覆盖行内代码样式，让 hljs 高亮生效 */
.markdown-content :deep(pre code) {
  background: transparent !important;
  padding: 0 !important;
  border: none !important;
  font-size: 13px !important;
  display: block;
  line-height: 1.6;
  /* 不设置 color，让 hljs 的样式生效 */
}

/* 确保 highlight.js 的样式生效 */
.markdown-content :deep(pre code.hljs) {
  background: transparent;
}

.markdown-content :deep(.hljs) {
  background: transparent;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 16px;
  margin: 12px 0;
  color: #666;
  background: #f9f9f9;
  padding: 12px 16px;
  border-radius: 4px;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content :deep(th) {
  background: #f5f5f5;
  font-weight: 600;
}

.markdown-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #e0e0e0;
  margin: 16px 0;
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
  padding: 8px 0;
  align-items: center;
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
